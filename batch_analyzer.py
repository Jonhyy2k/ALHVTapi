import time
import pandas as pd
import argparse
from alpha_vantage_client import AlphaVantageClient
from advanced_quant_functions_backup import calculate_sigma, get_sigma_recommendation
from main import analyze_stock, append_stock_result, initialize_output_file

# Alpha Vantage API key
ALPHA_VANTAGE_API_KEY = "73KWO176IRABCOCJ"

# Output file
OUTPUT_FILE = "BATCH_ANALYSIS_RESULTS.txt"

def analyze_stock_batch(symbols):
    """
    Analyze a batch of stocks one by one
    
    Parameters:
    -----------
    symbols: list
        List of stock symbols to analyze
    
    Returns:
    --------
    dict
        Results summary
    """
    # Create Alpha Vantage client
    client = AlphaVantageClient(ALPHA_VANTAGE_API_KEY)
    
    # Initialize output file
    initialize_output_file()
    
    results_summary = {
        "total": len(symbols),
        "successful": 0,
        "failed": 0,
        "stocks": []
    }
    
    print(f"[INFO] Starting batch analysis of {len(symbols)} stocks")
    
    for i, symbol in enumerate(symbols):
        print(f"\n[INFO] Processing stock {i+1}/{len(symbols)}: {symbol}")
        
        # Analyze the stock
        result = analyze_stock(symbol, client)
        
        if result:
            # Append the result to the output file
            append_stock_result(result)
            print(f"[INFO] Analysis for {symbol} completed and saved to {OUTPUT_FILE}")
            
            # Add to summary
            results_summary["successful"] += 1
            results_summary["stocks"].append({
                "symbol": symbol,
                "sigma": result["sigma"],
                "price": result["price"],
                "recommendation": result["recommendation"].split(" - ")[0]  # Just the base recommendation
            })
        else:
            print(f"[WARNING] Analysis for {symbol} failed")
            results_summary["failed"] += 1
    
    # Sort results by sigma
    results_summary["stocks"] = sorted(
        results_summary["stocks"], 
        key=lambda x: x["sigma"], 
        reverse=True
    )
    
    # Print summary
    print("\n=== BATCH ANALYSIS COMPLETE ===")
    print(f"Total stocks analyzed: {results_summary['total']}")
    print(f"Successful analyses: {results_summary['successful']}")
    print(f"Failed analyses: {results_summary['failed']}")
    
    if results_summary["stocks"]:
        print("\nTop 5 stocks by Sigma score:")
        for i, stock in enumerate(results_summary["stocks"][:5]):
            print(f"{i+1}. {stock['symbol']} - Sigma: {stock['sigma']:.3f} - {stock['recommendation']}")
    
    return results_summary

def save_summary(results_summary, filename="batch_summary.csv"):
    """Save batch analysis summary to CSV file"""
    if not results_summary["stocks"]:
        print("[WARNING] No results to save")
        return
    
    try:
        df = pd.DataFrame(results_summary["stocks"])
        df.to_csv(filename, index=False)
        print(f"[INFO] Summary saved to {filename}")
    except Exception as e:
        print(f"[ERROR] Failed to save summary: {e}")

def main():
    """Main function for batch analysis"""
    parser = argparse.ArgumentParser(description="Batch Stock Analyzer")
    parser.add_argument("--symbols", type=str, help="Comma-separated list of stock symbols")
    parser.add_argument("--file", type=str, help="File with one symbol per line")
    parser.add_argument("--output", type=str, default="batch_summary.csv", help="Output summary file")
    
    args = parser.parse_args()
    
    if args.symbols:
        symbols = [s.strip().upper() for s in args.symbols.split(",")]
    elif args.file:
        try:
            with open(args.file, 'r') as f:
                symbols = [line.strip().upper() for line in f if line.strip()]
        except Exception as e:
            print(f"[ERROR] Failed to read symbols file: {e}")
            return
    else:
        print("[ERROR] Please provide symbols using --symbols or --file")
        return
    
    if not symbols:
        print("[ERROR] No valid symbols provided")
        return
    
    print(f"[INFO] Preparing to analyze {len(symbols)} stocks")
    
    # Run the batch analysis
    results = analyze_stock_batch(symbols)
    
    # Save summary to CSV
    save_summary(results, args.output)

if __name__ == "__main__":
    main()
