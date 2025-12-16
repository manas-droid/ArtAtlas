import argparse
from met_data_collection.load_data import save_batched_list_of_artworks

def main():
    parser = argparse.ArgumentParser(
        description="A script to save a batched list of artworks by department ID and a limit.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "dept_id",
        type=int,
        help="The required department ID for fetching artworks."
    )

    parser.add_argument(
        "-l", "--limit",
        type=int,
        default=3000,
        help="The maximum number of artworks to fetch. (Default: 3000)"
    )

    args = parser.parse_args()

    save_batched_list_of_artworks(
        dept_id=args.dept_id,
        limit=args.limit
    )

if __name__ == "__main__":
    main()