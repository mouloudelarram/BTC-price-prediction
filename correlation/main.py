from time import sleep


def monitor():
    # call lagged correlation to create new summary file for today
    from laggedCorrelationAnalysis import main
    summary_path = main()
    # make decision based on the new summary file
    from decisionEngine import BTCAutoTraderV3
    engine = BTCAutoTraderV3(summary_path)
    result = engine.run()
    # save decision result to csv file
    with open("decisions.csv", "a") as f:
        f.write(f"{result['timestamp'][:10]},{result['signal']}\n")
        
if __name__ == "__main__":
    while True:
        monitor()
        # wait for 24 hours before next check
        sleep(24 * 60 * 60)