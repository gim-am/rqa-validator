import argparse
from pathlib import Path
from src.rqa_validator.orchestrator.validation_pipeline import ValidationPipeline

def main():
    parser = argparse.ArgumentParser(description="Data Validation Framework")
    parser.add_argument("input_file", type=Path, help="Path to Excel file")
    parser.add_argument("--dataset-type", required=True, 
                       choices=["jmmi"],
                       help="Type of dataset to validate")
    # parser.add_argument("--output", type=Path, default=Path("validation_results.json"),
    #                    help="Output path for JSON results")
    
    args = parser.parse_args()

    pipeline = ValidationPipeline(dataset_type=args.dataset_type)
    results = pipeline.run(args.input_file)

    print(f"Admin Errors: {results['summary']['admin_errors']}")
    print(f"Errors: {results['summary']['errors']}")
    print(f"Warnings: {results['summary']['warnings']}")
    print(f"info: {results['summary']['info']}")
    print(results['admin_errors'])
    print(results['errors'])
    print(results['warnings'])
    print(results['info'])

if __name__ == "__main__":
    exit(main())
