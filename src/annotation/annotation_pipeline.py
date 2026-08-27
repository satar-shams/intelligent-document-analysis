from src.annotation.analyze_dataset import analyze_dataset
from src.annotation.apply_annotations import apply_annotations
from src.annotation.create_dataset import main as create_dataset
from src.annotation.split_dataset import main as split_dataset
from src.annotation.validate_dataset import validate_dataset


def main() -> None:
    print("=" * 60)
    print("ANNOTATION PIPELINE")
    print("=" * 60)

    print("\n[1/5] Creating annotation dataset...")
    create_dataset()

    print("\n[2/5] Applying automatic annotations...")
    apply_annotations()

    print("\n[3/5] Validating annotation dataset...")
    total_chunks, total_entities, errors = validate_dataset()

    print(f"Validated chunks: {total_chunks}")
    print(f"Validated entities: {total_entities}")
    print(f"Validation errors: {len(errors)}")

    if errors:
        print("\nAnnotation pipeline stopped.")
        print("Validation failed:")

        for error in errors:
            print(f"- {error}")

        raise SystemExit(1)

    print("\nValidation successful.")

    print("\n[4/5] Analyzing annotation dataset...")
    analyze_dataset()

    print("\n[5/5] Splitting annotation dataset...")
    split_dataset()

    print("\n" + "=" * 60)
    print("ANNOTATION PIPELINE COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()