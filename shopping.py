import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

import numpy as np
import pandas as pd

TEST_SIZE = 0.4


def main():
    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """

    # Load data
    df = pd.read_csv(filename)

    # Create mappings of months and visitor types
    months = {"Jan": 0,
              "Feb": 1,
              "Mar": 3,
              "Apr": 4,
              "May": 5,
              "June": 6,
              "Jul": 7,
              "Aug": 8,
              "Sep": 9,
              "Oct": 10,
              "Nov": 11,
              "Dec": 12}

    visitors = {"New_Visitor": 0,
                "Returning_Visitor": 1,
                "Other": 0}

    # Get labels for individual datapoints
    labels = df['Revenue'].astype(int).tolist()

    # Create data points as formatted lists of values, floats get rounded to two decimals
    df['Administrative'] = df['Administrative'].astype(int)
    df['Administrative_Duration'] = df['Administrative_Duration'].astype(float).round(2)
    df['Informational'] = df['Informational'].astype(int).round(2)
    df['Informational_Duration'] = df['Informational_Duration'].astype(float).round(2)
    df['ProductRelated'] = df['ProductRelated'].astype(int)
    df['ProductRelated_Duration'] = df['ProductRelated_Duration'].astype(float).round(2)
    df['BounceRates'] = df['BounceRates'].astype(float).round(2)
    df['ExitRates'] = df['ExitRates'].astype(float).round(2)
    df['PageValues'] = df['PageValues'].astype(float).round(2)
    df['SpecialDay'] = df['SpecialDay'].astype(float).round(2)
    df['Month'] = df['Month'].map(months)
    df['OperatingSystems'] = df['OperatingSystems'].astype(int)
    df['Browser'] = df['Browser'].astype(int)
    df['Region'] = df['Region'].astype(int)
    df['TrafficType'] = df['TrafficType'].astype(int)
    df['VisitorType'] = df['VisitorType'].map(visitors)
    df['Weekend'] = df['Weekend'].astype(int)
    del df['Revenue']

    # Init result
    evidence = df.values.tolist()
    result = [evidence, labels]

    # Return a tuple (evidence, labels).
    return result


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(evidence, labels)
    return model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificity).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """

    # Positive and positive identified count
    pos = 0
    posid = 0

    # Negative and positive identified count
    neg = 0
    negid = 0

    for label, pred in zip(labels, predictions):
        if label == 1:
            pos += 1
            if pred == 1:
                posid += 1
        elif label == 0:
            neg += 1
            if pred == 0:
                negid += 1
        else:
            raise ValueError

    # `sensitivity` should be a floating-point value from 0 to 1
    #     representing the "true positive rate": the proportion of
    #     actual positive labels that were accurately identified.
    sens = float(posid / pos)

    # `specificity` should be a floating-point value from 0 to 1
    #     representing the "true negative rate": the proportion of
    #     actual negative labels that were accurately identified.
    spec = float(negid / neg)

    return (sens, spec)


def clean_dataset(df):
    assert isinstance(df, pd.DataFrame), "df needs to be a pd.DataFrame"
    df.dropna(inplace=True)
    indices_to_keep = ~df.isin([np.nan, np.inf, -np.inf]).any(1)
    return df[indices_to_keep].astype(np.float64)


if __name__ == "__main__":
    main()
