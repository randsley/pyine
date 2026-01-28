"""Async usage examples for the pyptine library.

This module demonstrates how to use the AsyncINE client for non-blocking I/O
and concurrent API requests.
"""

import asyncio
from pyptine import AsyncINE


async def example_1_basic_async() -> None:
    """Example 1: Basic async usage with context manager."""
    print("=" * 60)
    print("Example 1: Basic Async Usage")
    print("=" * 60)

    async with AsyncINE(language="EN") as ine:
        # Fetch single indicator
        response = await ine.get_data("0004167")
        df = response.to_dataframe()
        print(f"Fetched data for indicator 0004167")
        print(f"Data shape: {df.shape}")
        print(f"First 5 rows:")
        print(df.head())


async def example_2_concurrent_requests() -> None:
    """Example 2: Fetch multiple indicators concurrently."""
    print("\n" + "=" * 60)
    print("Example 2: Concurrent Requests")
    print("=" * 60)

    async with AsyncINE(language="EN") as ine:
        # Fetch multiple indicators concurrently
        print("Fetching 3 indicators concurrently...")
        responses = await asyncio.gather(
            ine.get_data("0004167"),  # Resident population
            ine.get_data("0004127"),  # GDP
            ine.get_data("0008074"),  # Unemployment rate
        )

        print(f"\nSuccessfully fetched {len(responses)} indicators:")
        for i, response in enumerate(responses, 1):
            df = response.to_dataframe()
            print(f"  {i}. Indicator: {response.varcd}, Data points: {len(df)}")


async def example_3_async_search() -> None:
    """Example 3: Async search operations."""
    print("\n" + "=" * 60)
    print("Example 3: Async Search")
    print("=" * 60)

    async with AsyncINE(language="EN") as ine:
        # Search for indicators
        print("Searching for 'gdp' indicators...")
        results = await ine.search("gdp")  # type: ignore[attr-defined]
        print(f"Found {len(results)} indicators")

        # Display first 5 results
        print("\nTop 5 results:")
        for indicator in results[:5]:
            print(f"  - {indicator.varcd}: {indicator.title}")


async def example_4_async_metadata() -> None:
    """Example 4: Fetch metadata asynchronously."""
    print("\n" + "=" * 60)
    print("Example 4: Async Metadata Fetching")
    print("=" * 60)

    async with AsyncINE(language="EN") as ine:
        # Fetch metadata concurrently
        print("Fetching metadata for multiple indicators...")
        metadata_list = await asyncio.gather(
            ine.get_metadata("0004167"),
            ine.get_metadata("0004127"),
            ine.get_metadata("0008074"),
        )

        print(f"\nMetadata for {len(metadata_list)} indicators:")
        for metadata in metadata_list:
            print(f"\n  {metadata.varcd}: {metadata.title}")
            print(f"    - Unit: {metadata.unit}")
            print(f"    - Dimensions: {len(metadata.dimensions)}")


async def example_5_streaming_large_dataset() -> None:
    """Example 5: Stream large datasets with async iterator."""
    print("\n" + "=" * 60)
    print("Example 5: Streaming Large Datasets")
    print("=" * 60)

    async with AsyncINE(language="EN") as ine:
        print("Streaming data in chunks...")
        total_rows = 0
        chunk_count = 0

        # Stream large dataset in chunks
        async for chunk in ine.get_all_data("0004127", chunk_size=10000):
            chunk_count += 1
            df_chunk = chunk.to_dataframe()
            total_rows += len(df_chunk)
            print(f"  Chunk {chunk_count}: {len(df_chunk)} rows")

        print(f"\nTotal rows processed: {total_rows}")
        print(f"Total chunks: {chunk_count}")


async def example_6_error_handling() -> None:
    """Example 6: Error handling in async operations."""
    print("\n" + "=" * 60)
    print("Example 6: Error Handling")
    print("=" * 60)

    async with AsyncINE(language="EN") as ine:
        # Try to fetch an invalid indicator
        try:
            print("Attempting to fetch invalid indicator...")
            response = await ine.get_data("9999999")
            print(f"Response: {response}")
        except Exception as e:
            print(f"Caught expected error: {type(e).__name__}")
            print(f"Error message: {str(e)}")

        # Continue with valid request
        print("\nFetching valid indicator...")
        response = await ine.get_data("0004167")
        print(f"Successfully fetched indicator {response.varcd}")


async def example_7_batch_processing() -> None:
    """Example 7: Batch process multiple search queries."""
    print("\n" + "=" * 60)
    print("Example 7: Batch Processing")
    print("=" * 60)

    async with AsyncINE(language="EN") as ine:
        # Search for multiple terms concurrently
        search_terms = ["population", "gdp", "employment", "inflation"]
        print(f"Searching for {len(search_terms)} terms concurrently...")

        tasks = [ine.search(term) for term in search_terms]  # type: ignore[attr-defined]
        results = await asyncio.gather(*tasks)

        print("\nSearch results:")
        for term, result_list in zip(search_terms, results):
            print(f"  '{term}': {len(result_list)} indicators found")


async def example_8_async_with_dimensions() -> None:
    """Example 8: Fetch data with dimension filters asynchronously."""
    print("\n" + "=" * 60)
    print("Example 8: Async with Dimension Filters")
    print("=" * 60)

    async with AsyncINE(language="EN") as ine:
        # Fetch data for multiple years concurrently
        print("Fetching population data for multiple years...")
        years = ["S7A2020", "S7A2021", "S7A2022", "S7A2023"]

        tasks = [ine.get_data("0004167", dimensions={"Dim1": year, "Dim2": "PT"}) for year in years]

        responses = await asyncio.gather(*tasks)

        print(f"\nFetched data for {len(responses)} years:")
        for response in responses:
            df = response.to_dataframe()
            print(f"  Year data: {len(df)} rows")


async def example_9_async_export() -> None:
    """Example 9: Export data asynchronously."""
    print("\n" + "=" * 60)
    print("Example 9: Async Export")
    print("=" * 60)

    async with AsyncINE(language="EN") as ine:
        # Fetch data
        print("Fetching data for export...")
        response = await ine.get_data("0004167", dimensions={"Dim1": "S7A2023"})

        # Convert to DataFrame
        df = response.to_dataframe()
        print(f"Data fetched: {len(df)} rows")

        # Export to CSV (note: export operations are synchronous)
        output_file = "async_export_example.csv"
        response.to_csv(output_file)
        print(f"Data exported to {output_file}")


async def example_10_performance_comparison() -> None:
    """Example 10: Compare async vs sequential performance."""
    print("\n" + "=" * 60)
    print("Example 10: Performance Comparison")
    print("=" * 60)

    indicators = ["0004167", "0004127", "0008074", "0007533", "0011776"]

    async with AsyncINE(language="EN") as ine:
        # Measure concurrent performance
        import time

        start_time = time.time()
        responses = await asyncio.gather(*[ine.get_data(code) for code in indicators])
        concurrent_time = time.time() - start_time

        print(f"Fetched {len(responses)} indicators concurrently")
        print(f"Time taken (concurrent): {concurrent_time:.2f} seconds")
        print(f"Average per indicator: {concurrent_time / len(indicators):.2f} seconds")


async def main() -> None:
    """Run all async examples."""
    print("\n" + "=" * 80)
    print("PYPTINE ASYNC EXAMPLES")
    print("=" * 80)

    await example_1_basic_async()
    await example_2_concurrent_requests()
    await example_3_async_search()
    await example_4_async_metadata()
    await example_5_streaming_large_dataset()
    await example_6_error_handling()
    await example_7_batch_processing()
    await example_8_async_with_dimensions()
    await example_9_async_export()
    await example_10_performance_comparison()

    print("\n" + "=" * 80)
    print("All async examples completed!")
    print("=" * 80)


if __name__ == "__main__":
    # Run all examples
    asyncio.run(main())
