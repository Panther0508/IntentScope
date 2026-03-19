"""
Hugging Face AI Service Module for IntentScope
Provides AI-powered text analysis, summarization, and generation capabilities
"""

import logging
import os

logger = logging.getLogger(__name__)

# Hugging Face Configuration
# Set HF_TOKEN environment variable for authenticated requests
# Get token from: https://huggingface.co/settings/tokens
HF_TOKEN = os.environ.get('HF_TOKEN', os.environ.get('HUGGING_FACE_HUB_TOKEN', None))

if HF_TOKEN:
    logger.info("Hugging Face token detected - authenticated mode enabled")

# Hugging Face AI Model Integration
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    logger.warning("Hugging Face transformers not available. AI features disabled.")

# AI Model instances (lazy loaded)
ai_summarizer = None
ai_sentiment_analyzer = None
ai_text_generator = None
ai_qa_model = None


def get_hf_token():
    """Get Hugging Face token for authenticated requests"""
    return HF_TOKEN


def get_summarizer():
    """Get or initialize the summarization model"""
    global ai_summarizer
    if ai_summarizer is None and HF_AVAILABLE:
        try:
            # Use a lightweight model for production
            ai_summarizer = pipeline(
                "summarization", 
                model="facebook/bart-large-cnn",
                model_kwargs={"torch_dtype": "float32"}
            )
            logger.info("Summarization model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load summarizer: {e}")
            ai_summarizer = None
    return ai_summarizer


def get_sentiment_analyzer():
    """Get or initialize the sentiment analysis model"""
    global ai_sentiment_analyzer
    if ai_sentiment_analyzer is None and HF_AVAILABLE:
        try:
            ai_sentiment_analyzer = pipeline(
                "sentiment-analysis", 
                model="distilbert-base-uncased-finetuned-sst-2-english"
            )
            logger.info("Sentiment analysis model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load sentiment analyzer: {e}")
            ai_sentiment_analyzer = None
    return ai_sentiment_analyzer


def get_text_generator():
    """Get or initialize the text generation model"""
    global ai_text_generator
    if ai_text_generator is None and HF_AVAILABLE:
        try:
            ai_text_generator = pipeline(
                "text-generation", 
                model="gpt2",
                max_new_tokens=100
            )
            logger.info("Text generation model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load text generator: {e}")
            ai_text_generator = None
    return ai_text_generator


def get_qa_model():
    """Get or initialize the question answering model"""
    global ai_qa_model
    if ai_qa_model is None and HF_AVAILABLE:
        try:
            ai_qa_model = pipeline(
                "question-answering", 
                model="distilbert-base-uncased-distilled-squad"
            )
            logger.info("Question answering model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load QA model: {e}")
            ai_qa_model = None
    return ai_qa_model


def summarize_text(text, max_length=150, min_length=40):
    """
    Summarize text using the BART model
    
    Args:
        text: Input text to summarize
        max_length: Maximum length of summary
        min_length: Minimum length of summary
    
    Returns:
        dict with summary text and metadata
    """
    if not HF_AVAILABLE:
        return {
            "success": False,
            "error": "Hugging Face transformers not installed",
            "summary": None
        }
    
    try:
        summarizer = get_summarizer()
        if summarizer is None:
            return {
                "success": False,
                "error": "Failed to load summarization model",
                "summary": None
            }
        
        # Truncate very long texts
        if len(text) > 4000:
            text = text[:4000]
        
        result = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
        
        return {
            "success": True,
            "summary": result[0]['summary_text'],
            "original_length": len(text),
            "summary_length": len(result[0]['summary_text']),
            "model": "facebook/bart-large-cnn"
        }
    except Exception as e:
        logger.error(f"Summarization error: {e}")
        return {
            "success": False,
            "error": str(e),
            "summary": None
        }


def analyze_sentiment(text):
    """
    Analyze sentiment of text
    
    Args:
        text: Input text to analyze
    
    Returns:
        dict with sentiment label and score
    """
    if not HF_AVAILABLE:
        return {
            "success": False,
            "error": "Hugging Face transformers not installed",
            "sentiment": None
        }
    
    try:
        analyzer = get_sentiment_analyzer()
        if analyzer is None:
            return {
                "success": False,
                "error": "Failed to load sentiment analyzer",
                "sentiment": None
            }
        
        # Truncate very long texts
        if len(text) > 512:
            text = text[:512]
        
        result = analyzer(text)[0]
        
        return {
            "success": True,
            "sentiment": result['label'],
            "score": round(result['score'], 4),
            "model": "distilbert-base-uncased-finetuned-sst-2-english"
        }
    except Exception as e:
        logger.error(f"Sentiment analysis error: {e}")
        return {
            "success": False,
            "error": str(e),
            "sentiment": None
        }


def generate_text(prompt, max_new_tokens=100, temperature=0.9, top_p=0.95):
    """
    Generate text based on a prompt
    
    Args:
        prompt: Input prompt for text generation
        max_new_tokens: Maximum tokens to generate
        temperature: Sampling temperature (0-1)
        top_p: Nucleus sampling parameter
    
    Returns:
        dict with generated text and metadata
    """
    if not HF_AVAILABLE:
        return {
            "success": False,
            "error": "Hugging Face transformers not installed",
            "generated_text": None
        }
    
    try:
        generator = get_text_generator()
        if generator is None:
            return {
                "success": False,
                "error": "Failed to load text generator",
                "generated_text": None
            }
        
        result = generator(
            prompt, 
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            do_sample=True
        )
        
        return {
            "success": True,
            "generated_text": result[0]['generated_text'],
            "prompt": prompt,
            "tokens_generated": len(result[0]['generated_text']) - len(prompt),
            "model": "gpt2"
        }
    except Exception as e:
        logger.error(f"Text generation error: {e}")
        return {
            "success": False,
            "error": str(e),
            "generated_text": None
        }


def answer_question(context, question):
    """
    Answer a question based on provided context
    
    Args:
        context: Context text to extract answer from
        question: Question to answer
    
    Returns:
        dict with answer and confidence score
    """
    if not HF_AVAILABLE:
        return {
            "success": False,
            "error": "Hugging Face transformers not installed",
            "answer": None
        }
    
    try:
        qa = get_qa_model()
        if qa is None:
            return {
                "success": False,
                "error": "Failed to load QA model",
                "answer": None
            }
        
        # Truncate very long contexts
        if len(context) > 2000:
            context = context[:2000]
        
        result = qa(question=question, context=context)
        
        return {
            "success": True,
            "answer": result['answer'],
            "score": round(result['score'], 4),
            "question": question,
            "model": "distilbert-base-uncased-distilled-squad"
        }
    except Exception as e:
        logger.error(f"Question answering error: {e}")
        return {
            "success": False,
            "error": str(e),
            "answer": None
        }


def get_ai_status():
    """
    Get the status of AI models
    
    Returns:
        dict with model availability status
    """
    return {
        "hf_available": HF_AVAILABLE,
        "models": {
            "summarizer": get_summarizer() is not None,
            "sentiment_analyzer": get_sentiment_analyzer() is not None,
            "text_generator": get_text_generator() is not None,
            "qa_model": get_qa_model() is not None
        }
    }
