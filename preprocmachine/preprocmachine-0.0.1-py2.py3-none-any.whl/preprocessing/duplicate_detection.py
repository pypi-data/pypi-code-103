def apply_Exact_Duplicate_Detection(df, target, config={}, eval_method=lr_get_mse):
    processed_dataset = df.drop_duplicates()

    try:
        dataframe, mse = eval_method(processed_dataset, target)
        return processed_dataset, mse
    except:
        return processed_dataset, float("inf")
