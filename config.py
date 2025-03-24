"""
Configuration file for the enhanced SAT Reading & Writing Chatbot Tutor

This file contains configuration settings for the Streamlit application.
"""

import os

# Create necessary directories
os.makedirs("data", exist_ok=True)
os.makedirs("data/sessions", exist_ok=True)
os.makedirs("data/performance", exist_ok=True)
os.makedirs("data/preferences", exist_ok=True)
os.makedirs("data/vocabulary", exist_ok=True)

# Streamlit configuration
STREAMLIT_CONFIG = {
    "theme": {
        "primaryColor": "#4CAF50",
        "backgroundColor": "#f5f5f5",
        "secondaryBackgroundColor": "#e0e0e0",
        "textColor": "#333333",
        "font": "sans serif"
    }
}

# Default vocabulary database
DEFAULT_VOCABULARY = {
    "prefixes": {
        "anti-": {"meaning": "against, opposite", "examples": ["antibiotic", "antisocial", "antithesis"]},
        "co-": {"meaning": "with, together", "examples": ["cooperate", "coexist", "coordinate"]},
        "de-": {"meaning": "down, away from", "examples": ["devalue", "decrease", "deactivate"]},
        "dis-": {"meaning": "not, opposite of", "examples": ["disagree", "dislike", "disconnect"]},
        "en-": {"meaning": "cause to, put into", "examples": ["enable", "enclose", "encourage"]},
        "fore-": {"meaning": "before, in front", "examples": ["foresee", "foreword", "forewarn"]},
        "in-": {"meaning": "not, into", "examples": ["invisible", "insert", "inaction"]},
        "inter-": {"meaning": "between, among", "examples": ["interact", "international", "intervene"]},
        "mis-": {"meaning": "wrongly", "examples": ["misunderstand", "misinterpret", "misinform"]},
        "non-": {"meaning": "not", "examples": ["nonfiction", "nonviolent", "nonsense"]},
        "over-": {"meaning": "excessive", "examples": ["overeat", "overconfident", "overestimate"]},
        "post-": {"meaning": "after", "examples": ["postgraduate", "postpone", "postscript"]},
        "pre-": {"meaning": "before", "examples": ["preview", "predict", "pretest"]},
        "re-": {"meaning": "again", "examples": ["rewrite", "rethink", "redo"]},
        "semi-": {"meaning": "half, partly", "examples": ["semicircle", "semifinal", "semiconductor"]},
        "sub-": {"meaning": "under", "examples": ["submarine", "submerge", "subtitle"]},
        "super-": {"meaning": "above, beyond", "examples": ["superhuman", "supernatural", "superpower"]},
        "trans-": {"meaning": "across, beyond", "examples": ["transport", "transform", "translate"]},
        "un-": {"meaning": "not, opposite of", "examples": ["unhappy", "unable", "unfair"]},
        "under-": {"meaning": "below, too little", "examples": ["underestimate", "underground", "underweight"]}
    },
    "roots": {
        "aud": {"meaning": "to hear", "examples": ["audible", "audience", "auditory"]},
        "bio": {"meaning": "life", "examples": ["biology", "biography", "biodiversity"]},
        "chron": {"meaning": "time", "examples": ["chronology", "chronic", "synchronize"]},
        "dict": {"meaning": "to say", "examples": ["dictate", "predict", "contradict"]},
        "duc/duct": {"meaning": "to lead", "examples": ["conduct", "induce", "production"]},
        "fac/fact": {"meaning": "to make, to do", "examples": ["factory", "manufacture", "artifact"]},
        "graph": {"meaning": "to write", "examples": ["photograph", "biography", "autograph"]},
        "ject": {"meaning": "to throw", "examples": ["reject", "inject", "projection"]},
        "jud": {"meaning": "to judge", "examples": ["judicial", "prejudice", "judgment"]},
        "log/logue": {"meaning": "word, study", "examples": ["biology", "dialogue", "monologue"]},
        "luc": {"meaning": "light", "examples": ["lucid", "translucent", "elucidate"]},
        "man": {"meaning": "hand", "examples": ["manual", "manufacture", "manuscript"]},
        "mit/miss": {"meaning": "to send", "examples": ["transmit", "mission", "admission"]},
        "mort": {"meaning": "death", "examples": ["mortal", "immortal", "mortician"]},
        "path": {"meaning": "feeling, suffering", "examples": ["sympathy", "pathology", "empathy"]},
        "ped": {"meaning": "foot, child", "examples": ["pedestrian", "pedal", "pediatrician"]},
        "phil": {"meaning": "love", "examples": ["philosophy", "philanthropy", "bibliophile"]},
        "phon": {"meaning": "sound", "examples": ["telephone", "symphony", "microphone"]},
        "port": {"meaning": "to carry", "examples": ["transport", "export", "portable"]},
        "scrib/script": {"meaning": "to write", "examples": ["describe", "manuscript", "inscription"]},
        "spec/spect": {"meaning": "to look", "examples": ["spectator", "inspect", "perspective"]},
        "struct": {"meaning": "to build", "examples": ["construct", "structure", "instruction"]},
        "tele": {"meaning": "distant", "examples": ["telephone", "television", "telescope"]},
        "terr": {"meaning": "earth, land", "examples": ["territory", "terrain", "terrestrial"]},
        "vac": {"meaning": "empty", "examples": ["vacant", "evacuate", "vacuum"]}
    },
    "suffixes": {
        "-able/-ible": {"meaning": "capable of being", "examples": ["readable", "flexible", "credible"]},
        "-al": {"meaning": "relating to", "examples": ["natural", "musical", "regional"]},
        "-ance/-ence": {"meaning": "state or quality of", "examples": ["importance", "independence", "confidence"]},
        "-ary": {"meaning": "connected with", "examples": ["dictionary", "library", "honorary"]},
        "-ate": {"meaning": "to make, become", "examples": ["activate", "create", "separate"]},
        "-ation": {"meaning": "process of", "examples": ["information", "creation", "celebration"]},
        "-cy": {"meaning": "state or quality", "examples": ["democracy", "accuracy", "privacy"]},
        "-dom": {"meaning": "state of being", "examples": ["freedom", "wisdom", "kingdom"]},
        "-er/-or": {"meaning": "person who", "examples": ["teacher", "actor", "visitor"]},
        "-ful": {"meaning": "full of", "examples": ["beautiful", "helpful", "careful"]},
        "-ic": {"meaning": "relating to", "examples": ["basic", "economic", "scientific"]},
        "-ion": {"meaning": "act or process", "examples": ["action", "connection", "discussion"]},
        "-ism": {"meaning": "doctrine, belief", "examples": ["capitalism", "optimism", "criticism"]},
        "-ist": {"meaning": "person who", "examples": ["artist", "scientist", "specialist"]},
        "-ity/-ty": {"meaning": "state or quality", "examples": ["activity", "equality", "reality"]},
        "-ive": {"meaning": "tending to", "examples": ["creative", "active", "sensitive"]},
        "-less": {"meaning": "without", "examples": ["homeless", "careless", "endless"]},
        "-ly": {"meaning": "in what manner", "examples": ["quickly", "carefully", "happily"]},
        "-ment": {"meaning": "action or process", "examples": ["development", "statement", "movement"]},
        "-ness": {"meaning": "state of being", "examples": ["happiness", "kindness", "darkness"]},
        "-ous": {"meaning": "full of", "examples": ["dangerous", "famous", "nervous"]},
        "-ship": {"meaning": "position held", "examples": ["friendship", "leadership", "relationship"]},
        "-sion/-tion": {"meaning": "state of being", "examples": ["tension", "action", "confusion"]},
        "-ward": {"meaning": "in the direction of", "examples": ["forward", "backward", "upward"]},
        "-y": {"meaning": "characterized by", "examples": ["happy", "sleepy", "funny"]}
    }
}

# Create default vocabulary file if it doesn't exist
import json
import os

if not os.path.exists("data/vocabulary/default_vocabulary.json"):
    os.makedirs("data/vocabulary", exist_ok=True)
    with open("data/vocabulary/default_vocabulary.json", "w") as f:
        json.dump(DEFAULT_VOCABULARY, f, indent=2)

# OpenAI API configuration
OPENAI_CONFIG = {
    "model": "gpt-4o",
    "embedding_model": "text-embedding-3-small",
    "temperature": 0.7,
    "max_tokens": 1000,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
}

# Memory configuration
MEMORY_CONFIG = {
    "max_tokens": 40000,
    "db_path": "data/memory.db",
    "embedding_dimension": 1536
}

# Question engine configuration
QUESTION_CONFIG = {
    "difficulty_levels": 5,
    "question_types": [
        "word_part_identification",
        "sentence_completion",
        "context_clue_analysis",
        "grammar"
    ],
    "reading_levels": range(8, 13)  # 8th grade to 12th grade
}

# Gamification configuration
GAMIFICATION_CONFIG = {
    "points_per_correct": 10,
    "streak_bonus_threshold": 3,
    "max_streak_bonus": 10,
    "achievements": [
        {"title": "Streak Starter", "description": "Answer 3 questions correctly in a row", "threshold": 3},
        {"title": "On Fire", "description": "Answer 5 questions correctly in a row", "threshold": 5},
        {"title": "Prefix Pro", "description": "Answer 10 prefix questions correctly", "threshold": 10},
        {"title": "Root Master", "description": "Answer 10 root questions correctly", "threshold": 10},
        {"title": "Suffix Sage", "description": "Answer 10 suffix questions correctly", "threshold": 10},
        {"title": "Vocabulary Virtuoso", "description": "Earn 100 points", "threshold": 100}
    ]
}
