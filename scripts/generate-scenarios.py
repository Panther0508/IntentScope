#!/usr/bin/env python3
import json, math, random, os

def gauss(mu, sigma):
    return random.gauss(mu, sigma)

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def make_scenario(name, duration, cfg):
    fps = 20
    frames = int(duration * fps)
    timestamps = [round(i/fps, 2) for i in range(frames)]
    scene = []
    for i in range(frames):
        t = i / fps
        phase = t * 0.5
        gaze_x = math.sin(phase) * 0.3 + math.sin(t*2.3) * 0.1
        gaze_y = math.cos(phase*0.7) * 0.2
        au = [clamp(math.sin(t*(0.5+j*0.2))*0.1 + (1.0 if random.random()<0.02 else 0), 0, 1.5) for j in range(6)]
        mfcc = [clamp(gauss(0,0.5), -2, 2) for _ in range(13)]
        pitch = clamp(0.3 + math.sin(t*1.5)*0.2 + random.random()*0.1, 0, 1)
        loud = clamp(0.4 + cfg['energy'] + math.sin(t*0.8)*0.2, 0, 1)
        jitter = clamp(random.random()*0.02, 0, 0.05)
        shimmer = clamp(random.random()*0.03, 0, 0.06)
        kbd = None
        if cfg['typing'] and random.random() < cfg['rate']:
            kbd = {
                'interKeyInterval': round(random.uniform(80,200),1),
                'holdDuration': round(random.uniform(40,120),1),
                'variance': round(random.uniform(10,50),1),
                'typingSpeed': round(random.uniform(40,80),1)
            }
        scene.append({
            'face': {'gaze_x': round(gaze_x,4), 'gaze_y': round(gaze_y,4), 'au': [round(a,4) for a in au]},
            'voice': {'mfcc': [round(m,4) for m in mfcc], 'pitch': round(pitch,4), 'loudness': round(loud,4), 'jitter': round(jitter,4), 'shimmer': round(shimmer,4)},
            'keyboard': kbd
        })
    return {'name': name, 'duration': duration, 'timestamps': timestamps, 'frames': scene, 'description': cfg.get('desc','')}

os.makedirs('public/scenarios', exist_ok=True)
scenarios = {
    'exploring.json': make_scenario('exploring', 12, {'energy':0.2, 'typing':True, 'rate':0.15, 'desc':'Curious browsing'}),
    'buy_intent.json': make_scenario('buy_intent', 10, {'energy':0.6, 'typing':True, 'rate':0.25, 'desc':'High excitement, focused'}),
    'deceptive_response.json': make_scenario('deceptive_response', 8, {'energy':0.4, 'typing':True, 'rate':0.08, 'desc':'Hesitation spikes'})
}
for fn, data in scenarios.items():
    path = os.path.join('public','scenarios',fn)
    with open(path,'w') as f:
        json.dump(data, f, indent=2)
    print(f'OK  {fn}  {len(data["frames"])} frames')
print('Done')
