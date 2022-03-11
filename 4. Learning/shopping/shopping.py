import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix

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
    evidence = []
    labels = []

    # Read in the data and clean it
    with open(filename) as csvfile:
        reader = list(csv.DictReader(csvfile))

        int_lst = [
            'Administrative',
            'Informational',
            'ProductRelated',
            'Month',
            'OperatingSystems',
            'Browser',
            'Region',
            'TrafficType',
            'VisitorType',
            'Weekend'
            ]

        flt_lst = [
            'Administrative_Duration',
            'Informational_Duration',
            'ProductRelated_Duration',
            'BounceRates',
            'ExitRates',
            'PageValues',
            'SpecialDay'
            ]

        month_dict = {
            'Jan': 0,
            'Feb': 1,
            'Mar': 2,
            'Apr': 3,
            'May': 4,
            'June': 5,
            'Jul': 6,
            'Aug': 7,
            'Sep': 8,
            'Oct': 9,
            'Nov': 10,
            'Dec': 11
            }

        for row in reader:
            # Set month to numerical value from dict
            row['Month'] = month_dict[row['Month']]
            row['VisitorType'] = 1 if row['VisitorType'] == 'Returning_Visitor' else 0
            row['Weekend'] = 1 if row['Weekend'] == 'TRUE' else 0
            row['Revenue'] = 1 if row['Revenue'] == 'TRUE' else 0
            # Typecast to int all items in int_lst
            for item in int_lst:
                row[item] = int(row[item])
            # Typecast to float all items in flt_lst
            for item in flt_lst:
                row[item] = float(row[item])

            # Append the cleaned data into the new lists
            evidence.append(list(row.values())[:-1])
            labels.append(list(row.values())[-1])

    return (evidence, labels)


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    # Choose the model and fit the data to the model
    model = KNeighborsClassifier(n_neighbors=1)
    return model.fit(evidence, labels)


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificty).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    # Scikit has a confusion_matrix function
    # https://scikit-learn.org/stable/modules/generated/sklearn.metrics.confusion_matrix.html#sklearn.metrics.confusion_matrix
    tn, fp, fn, tp = confusion_matrix(labels, predictions).ravel()

    # These equations are founds in the scikit documentation
    # https://scikit-learn.org/stable/modules/model_evaluation.html#confusion-matrix
    # Sensitivity is called "recall" in the docs
    sensitivity = tp / (tp + fn)
    specificity = tn / (tn + fp)

    return (sensitivity, specificity)


if __name__ == "__main__":
    main()
