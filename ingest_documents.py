"""
Document Ingestion Script
Batch process and add documents to the vector store
"""
import logging
from pathlib import Path
from typing import List
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from config import settings
from agents.rag_agent import get_vector_store, get_document_processor
from utils.logger import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


def read_text_file(file_path: Path) -> str:
    """Read text from a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        return ""


def ingest_documents_from_directory(directory: str, file_patterns: List[str] = None):
    """
    Ingest all documents from a directory
    
    Args:
        directory: Path to directory containing documents
        file_patterns: List of file patterns to match (e.g., ["*.txt", "*.md"])
    """
    if file_patterns is None:
        file_patterns = ["*.txt", "*.md"]
    
    dir_path = Path(directory)
    
    if not dir_path.exists():
        logger.error(f"Directory not found: {directory}")
        return
    
    # Get document processor and vector store
    processor = get_document_processor()
    vector_store = get_vector_store()
    
    total_files = 0
    total_chunks = 0
    
    # Process each file pattern
    for pattern in file_patterns:
        files = list(dir_path.glob(pattern))
        
        for file_path in files:
            logger.info(f"Processing: {file_path.name}")
            
            try:
                # Read file content
                content = read_text_file(file_path)
                
                if not content:
                    logger.warning(f"Empty file: {file_path.name}")
                    continue
                
                # Process into chunks
                metadata = {
                    "source": file_path.name,
                    "file_path": str(file_path),
                    "file_type": file_path.suffix
                }
                
                chunks = processor.process_text(content, metadata)
                
                # Add to vector store
                doc_ids = vector_store.add_documents(chunks)
                
                total_files += 1
                total_chunks += len(chunks)
                
                logger.info(f"✅ {file_path.name}: {len(chunks)} chunks added")
                
            except Exception as e:
                logger.error(f"❌ Error processing {file_path.name}: {e}")
    
    logger.info(f"\n{'='*60}")
    logger.info(f"📊 Ingestion Summary")
    logger.info(f"{'='*60}")
    logger.info(f"Files processed: {total_files}")
    logger.info(f"Total chunks created: {total_chunks}")
    logger.info(f"Collection size: {vector_store.get_collection_count()}")
    logger.info(f"{'='*60}\n")


def ingest_sample_medical_data():
    """Ingest sample medical knowledge"""
    
    logger.info("Adding sample medical knowledge to vector store...")
    
    processor = get_document_processor()
    vector_store = get_vector_store()
    
    # Sample medical information
    sample_docs = [
        {
            "content": """
Diabetes Mellitus Overview

Diabetes is a chronic condition characterized by elevated blood glucose levels. There are two main types:

Type 1 Diabetes:
- Autoimmune condition where the body doesn't produce insulin
- Usually diagnosed in children and young adults
- Requires insulin therapy
- Symptoms include frequent urination, excessive thirst, unexplained weight loss

Type 2 Diabetes:
- Most common form (90-95% of cases)
- Body becomes resistant to insulin or doesn't produce enough
- Often associated with obesity and sedentary lifestyle
- Can sometimes be managed with lifestyle changes and oral medications

Common symptoms of diabetes include:
- Increased thirst and urination
- Extreme fatigue
- Blurred vision
- Slow-healing wounds
- Tingling in hands or feet

Complications:
- Cardiovascular disease
- Nerve damage (neuropathy)
- Kidney damage (nephropathy)
- Eye damage (retinopathy)
- Foot problems

Management includes regular blood glucose monitoring, healthy diet, exercise, and medications as prescribed.
            """,
            "metadata": {"source": "diabetes_overview.txt", "topic": "diabetes", "category": "endocrinology"}
        },
        {
            "content": """
Hypertension (High Blood Pressure)

Hypertension is a condition where blood pressure is consistently elevated above normal levels.

Blood Pressure Categories:
- Normal: Less than 120/80 mmHg
- Elevated: 120-129/<80 mmHg
- Stage 1 Hypertension: 130-139/80-89 mmHg
- Stage 2 Hypertension: 140/90 mmHg or higher
- Hypertensive Crisis: Higher than 180/120 mmHg

Risk Factors:
- Age (risk increases with age)
- Family history
- Obesity
- Lack of physical activity
- High sodium diet
- Excessive alcohol consumption
- Stress
- Certain chronic conditions (diabetes, kidney disease)

Symptoms:
Often called the "silent killer" because most people have no symptoms. Some may experience:
- Headaches
- Shortness of breath
- Nosebleeds
- Dizziness

Complications:
- Heart attack
- Stroke
- Heart failure
- Kidney disease
- Vision problems

Treatment:
- Lifestyle modifications (diet, exercise, weight loss)
- Medications (ACE inhibitors, ARBs, diuretics, beta-blockers, calcium channel blockers)
- Regular blood pressure monitoring
            """,
            "metadata": {"source": "hypertension_guide.txt", "topic": "hypertension", "category": "cardiology"}
        },
        {
            "content": """
Common Cold vs. Flu

Understanding the difference between common cold and influenza:

Common Cold:
Causative agents: Rhinoviruses, coronaviruses
Onset: Gradual
Symptoms:
- Runny or stuffy nose
- Sore throat
- Mild cough
- Sneezing
- Mild body aches
- Low-grade fever (rare in adults)
Duration: 7-10 days
Treatment: Rest, fluids, over-the-counter symptom relief

Influenza (Flu):
Causative agent: Influenza viruses (A, B, C)
Onset: Sudden
Symptoms:
- High fever (100-104°F)
- Severe body aches
- Fatigue and weakness
- Dry cough
- Headache
- Chills
Duration: 1-2 weeks
Treatment: Antiviral medications (if started within 48 hours), rest, fluids

Prevention:
- Annual flu vaccination
- Frequent handwashing
- Avoiding close contact with sick individuals
- Covering mouth/nose when coughing or sneezing
- Staying home when sick

When to seek medical care:
- Difficulty breathing
- Chest pain
- Persistent high fever
- Confusion
- Severe weakness
- Symptoms that improve then worsen
            """,
            "metadata": {"source": "cold_vs_flu.txt", "topic": "respiratory infections", "category": "infectious disease"}
        }
    ]
    
    total_chunks = 0
    
    for doc in sample_docs:
        chunks = processor.process_text(
            text=doc["content"],
            metadata=doc["metadata"]
        )
        vector_store.add_documents(chunks)
        total_chunks += len(chunks)
        logger.info(f"✅ Added {doc['metadata']['source']}: {len(chunks)} chunks")
    
    logger.info(f"\n{'='*60}")
    logger.info(f"📊 Sample Data Ingestion Complete")
    logger.info(f"{'='*60}")
    logger.info(f"Documents added: {len(sample_docs)}")
    logger.info(f"Total chunks: {total_chunks}")
    logger.info(f"Collection size: {vector_store.get_collection_count()}")
    logger.info(f"{'='*60}\n")


def main():
    """Main ingestion function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Ingest documents into medical assistant knowledge base")
    parser.add_argument("--directory", "-d", help="Directory containing documents to ingest")
    parser.add_argument("--sample", "-s", action="store_true", help="Ingest sample medical data")
    parser.add_argument("--patterns", "-p", nargs="+", default=["*.txt", "*.md"], 
                       help="File patterns to match (e.g., *.txt *.md)")
    
    args = parser.parse_args()
    
    if args.sample:
        ingest_sample_medical_data()
    elif args.directory:
        ingest_documents_from_directory(args.directory, args.patterns)
    else:
        print("Please specify --directory or --sample")
        parser.print_help()


if __name__ == "__main__":
    main()
