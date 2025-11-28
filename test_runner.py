
import app as main_app

# Set the app context to be able to use url_for
with main_app.app.app_context():
    print("--- Running Comprehensive Analysis on Dummy Data ---")
    
    # Define the paths to the dummy files
    filepath1 = 'dummy_2024_all_dims.csv'
    filepath2 = 'dummy_2025_all_dims.csv'
    
    # Run the analysis function directly
    insights, charts = main_app.run_comprehensive_analysis(filepath1, filepath2)
    
    print("\n--- Generated Insights ---")
    if insights:
        for i, insight in enumerate(insights):
            print(f"{i+1}. {insight}")
    else:
        print("No insights were generated.")
        
    print("\n--- Generated Charts ---")
    if charts:
        for i, chart in enumerate(charts):
            print(f"{i+1}. Title: {chart['title']}, Chart Filename: {chart['chart_filename']}")
    else:
        print("No charts were generated.")

print("\n--- Test finished. ---")
