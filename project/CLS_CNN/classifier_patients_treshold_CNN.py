import pickle
import numpy as np
from collections import Counter
from sklearn.metrics import classification_report
from sklearn import metrics
from sklearn import tree
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import GradientBoostingClassifier
import matplotlib.pyplot as plt
def process_data(data, patients_id, labels_ids, lable2num2classes, lable2num3classes):
    """
    data: dictionary of each patient with the labels of each image patch

    return: X, y
    """
    new_data = {}
    for patient, labels in data.items():
        new_data[patient] = Counter(labels)
        total = sum(new_data[patient].values())
        for i in range(3):
            if i not in new_data[patient].keys():
                new_data[patient][i] = 0
            new_data[patient][i] /= total
        
        new_data[patient]["value"] = new_data[patient][1]

    X = []
    y = []
    y3 = []
    for patient, label in zip(patients_id, labels_ids):
        if patient in new_data.keys():
            # print(patient, label)
            # print(new_data[patient]["value"], lable2num[label])
            X.append(new_data[patient]["value"])
            y.append(lable2num2classes[label])
            y3.append(lable2num3classes[label])

    return np.array(X), np.array(y), np.array(y3)


if __name__ == '__main__':
    path_train_data  = "/fhome/gia07/project/runs_clf/efficientnet-2c/Ground_truth_patient_classification/dict_train_cropped_positive_negative.pkl"
    path_test_data  = "/fhome/gia07/project/runs_clf/efficientnet-2c/Ground_truth_patient_classification/dict_test_cropped_positive_negative.pkl"
    path_train_labels = "/fhome/gia07/project/Train_test_splits/train_data.pkl"
    path_test_labels = "/fhome/gia07/project/Train_test_splits/test_data.pkl"

    lable2num_2clases = {"NEGATIVA":0, "BAIXA":1, "ALTA":1}
    lable2num_3clases = {"NEGATIVA":0, "BAIXA":1, "ALTA":2}

    with open(path_train_data, 'rb') as file:
        dict_train = pickle.load(file)

    print(len(dict_train["prediction"].keys()))
    with open(path_test_data, 'rb') as file:
        dict_test = pickle.load(file)
    
    print(len(dict_test["prediction"].keys()))
    # Use the model predictions
    train_data = dict_train["prediction"]
    test_data = dict_test["prediction"]

    for pacient in train_data.keys():
        train_data[pacient] = np.array(train_data[pacient]).reshape(-1)
    
    for pacient in test_data.keys():
        test_data[pacient] = np.array(test_data[pacient]).reshape(-1)

    with open(path_train_labels, 'rb') as file:
        patients_id_train, train_labels = pickle.load(file)
    with open(path_test_labels, 'rb') as file:
        patients_id_test, test_labels = pickle.load(file)

        
    X_train, y_train, y_train_3 = process_data(train_data, patients_id_train, train_labels, 
                                    lable2num2classes=lable2num_2clases, lable2num3classes=lable2num_3clases)
    X_test, y_test, y_test_3 = process_data(test_data, patients_id_test, test_labels, 
                                    lable2num2classes=lable2num_2clases, lable2num3classes=lable2num_3clases)

    print(len(X_train), len(X_test), len(y_train), len(y_test))
    # K-folds cross validation
    from sklearn.model_selection import StratifiedKFold, KFold
    kf = KFold(n_splits=8)
    kf = StratifiedKFold(n_splits=5)
    dict_splits_results_pos_neg = {}
    dict_splits_results_high_low = {}

    best_thresholds_neg_pos = []
    best_thresholds_high_low = []
    for i, (train_index, test_index) in enumerate(kf.split(X_train, y=y_train)):
        # print("TRAIN:", train_index, "TEST:", test_index)
        X_train2, X_test2 = X_train[train_index], X_train[test_index]
        y_train2, y_train2_3, y_test2, y_test2_3 = y_train[train_index], y_train_3[train_index], y_train[test_index], y_train_3[test_index]

        fpr, tpr, thresholds = metrics.roc_curve(y_train2, X_train2, pos_label=1)
        # plt.plot(fpr, tpr)
        # plt.xlabel("False positive rate")
        # plt.ylabel("True positive rate")
        # plt.savefig("roc_curve_pos_neg.png")
        # plt.close()

        # Get the treshold that has higher true positive rate and lower false positive rate
        best_treshold = 0
        best_distance = 100
        for i in range(len(fpr)):
            distance = np.sqrt(fpr[i]**2 + (1 - tpr[i])**2)
            if distance < best_distance:
                best_distance = distance
                best_treshold = thresholds[i]
        
        best_thresholds_neg_pos.append(best_treshold)


        y_pred2 = np.where(X_test2 > best_treshold, 1, 0)

        dict_splits_results_pos_neg[f"split_{i}_val"] = classification_report(y_test2, y_pred2, target_names=["Negative", "Positive"], output_dict=True)

        # Split the positive cases into high and low
        X_train_positve = X_train2[y_train2 == 1]
        y_train_positve = y_train2_3[y_train2 == 1] - 1


        fpr, tpr, thresholds = metrics.roc_curve(y_train_positve, X_train_positve, pos_label=1)
        # plt.plot(fpr, tpr)
        # plt.xlabel("False positive rate")
        # plt.ylabel("True positive rate")
        # plt.savefig("roc_curve_high_low.png")

        # Get the treshold that has higher true positive rate and lower false positive rate
        best_treshold_high_low = 0
        best_distance = 100
        for i in range(len(fpr)):
            distance = np.sqrt(fpr[i]**2 + (1 - tpr[i])**2)
            if distance < best_distance:
                best_distance = distance
                best_treshold_high_low = thresholds[i]

        best_thresholds_high_low.append(best_treshold_high_low)

        y_pred2 = np.where(X_test2 > best_treshold_high_low, 2, y_pred2)

        dict_splits_results_high_low[f"split_{i}_val"] = classification_report(y_test2_3, y_pred2, target_names=["Negative", "Low", "High"], output_dict=True)
        
    best_threshold_neg_pos = np.median(best_thresholds_neg_pos)
    best_threshold_high_low = np.median(best_thresholds_high_low)

    plt.figure(figsize=(6, 5))
    plt.boxplot((best_thresholds_neg_pos, best_thresholds_high_low), 
                showmeans=True, 
                meanline=True, 
                labels=["Treshold positive/negative", "Treshold high/low"])
    plt.ylabel("Treshold value")
    plt.savefig("boxplot_tresholds_patients.png")
    plt.close()

    print("2 CLASES:")
    print("Results k fold val")
    precision_neg = []
    precision_pos = []
    recall_neg = []
    recall_pos = []
    f1_neg = []
    f1_pos = []
    for key in dict_splits_results_pos_neg.keys():
        precision_neg.append(dict_splits_results_pos_neg[key]["Negative"]["precision"])
        precision_pos.append(dict_splits_results_pos_neg[key]["Positive"]["precision"])
        recall_neg.append(dict_splits_results_pos_neg[key]["Negative"]["recall"])
        recall_pos.append(dict_splits_results_pos_neg[key]["Positive"]["recall"])
        f1_neg.append(dict_splits_results_pos_neg[key]["Negative"]["f1-score"])
        f1_pos.append(dict_splits_results_pos_neg[key]["Positive"]["f1-score"])


    plt.figure(figsize=(10, 5))
    plt.boxplot((precision_neg, recall_neg, f1_neg, precision_pos, recall_pos, f1_pos), 
                showmeans=True, 
                meanline=True, 
                meanprops={'color': 'blue'},
                medianprops={'color': 'orange'},
                labels=["Precision Negative", "Recall Negative", "F1 Negative", "Precision Positive", "Recall Positive", "F1 Positive"])
    plt.ylabel("Metric value")
    plt.ylim(0, 1)
    plt.savefig("boxplot_metrics_pos_neg_patients.png")
    plt.close()

    print("Mean results k folds val:")
    print("Negative")
    print(f"Precision: {np.mean(precision_neg):.3} +- {np.std(precision_neg):.3}")
    print(f"Recall: {np.mean(recall_neg):.3} +- {np.std(recall_neg):.3}")
    print(f"F1: {np.mean(f1_neg):.3} +- {np.std(f1_neg):.3}")
    print("")
    print("Positive")
    print(f"Precision: {np.mean(precision_pos):.3} +- {np.std(precision_pos):.3}")
    print(f"Recall: {np.mean(recall_pos):.3} +- {np.std(recall_pos):.3}")
    print(f"F1: {np.mean(f1_pos):.3} +- {np.std(f1_pos):.3}")

    print("")
    print(f"Mean treshold: {np.mean(best_thresholds_neg_pos)} +- {np.std(best_thresholds_neg_pos)}")

    

    print("Results train 2 classes")
    y_pred = np.where(X_train > best_threshold_neg_pos, 1, 0)
    print(classification_report(y_train, y_pred, target_names=["Negative", "Positive"]))
    print("")
    # Predict the test data using both tresholds
    y_pred = np.where(X_test > best_treshold, 1, 0)
    print("Results test 2 classes")
    print(classification_report(y_test, y_pred, target_names=["Negative", "Positive"]))


    print("3 CLASES:")
    print("Results k fold val")
    precision_neg = []
    precision_low = []
    precision_high = []
    recall_neg = []
    recall_low = []
    recall_high = []
    f1_neg = []
    f1_low = []
    f1_high = []
    for key in dict_splits_results_high_low.keys():
        precision_neg.append(dict_splits_results_high_low[key]["Negative"]["precision"])
        precision_low.append(dict_splits_results_high_low[key]["Low"]["precision"])
        precision_high.append(dict_splits_results_high_low[key]["High"]["precision"])

        recall_neg.append(dict_splits_results_high_low[key]["Negative"]["recall"])
        recall_low.append(dict_splits_results_high_low[key]["Low"]["recall"])
        recall_high.append(dict_splits_results_high_low[key]["High"]["recall"])

        f1_neg.append(dict_splits_results_high_low[key]["Negative"]["f1-score"])
        f1_low.append(dict_splits_results_high_low[key]["Low"]["f1-score"])
        f1_high.append(dict_splits_results_high_low[key]["High"]["f1-score"])

    plt.figure(figsize=(10, 5))
    plt.boxplot((precision_high, recall_high, f1_high, precision_low, recall_low, f1_low), 
                showmeans=True, 
                meanline=True, 
                meanprops={'color': 'blue'},
                medianprops={'color': 'orange'},
                labels=["Precision High", "Recall High", "F1 High", "Precision Low", "Recall Low", "F1 Low"])
    plt.ylabel("Metric value")
    plt.ylim(0, 1)
    plt.savefig("boxplot_metrics_high_low_patients.png")
    plt.close()

    print("Mean results k folds val:")
    print("Negative")
    print(f"Precision: {np.mean(precision_neg):.3} +- {np.std(precision_neg):.3}")
    print(f"Recall: {np.mean(recall_neg):.3} +- {np.std(recall_neg):.3}")
    print(f"F1: {np.mean(f1_neg):.3} +- {np.std(f1_neg):.3}")
    print("")
    print("Low")
    print(f"Precision: {np.mean(precision_low):.3} +- {np.std(precision_low):.3}")
    print(f"Recall: {np.mean(recall_low):.3} +- {np.std(recall_low):.3}")
    print(f"F1: {np.mean(f1_low):.3} +- {np.std(f1_low):.3}")
    print("")
    print("High")
    print(f"Precision: {np.mean(precision_high):.3} +- {np.std(precision_high):.3}")
    print(f"Recall: {np.mean(recall_high):.3} +- {np.std(recall_high):.3}")
    print(f"F1: {np.mean(f1_high):.3} +- {np.std(f1_high):.3}")

    print("")
    print(f"Mean treshold: {np.mean(best_thresholds_high_low)} +- {np.std(best_thresholds_high_low)}")


    print("Results train 3 classes")
    y_pred = np.where(X_train > best_threshold_neg_pos, 1, 0)
    y_pred_3 = np.where(X_train > best_treshold_high_low, 2, y_pred)
    print(classification_report(y_train_3, y_pred_3, target_names=["Negative", "Low", "High"]))
    print("")
    print("Results test 3 classes")
    y_pred = np.where(X_test > best_treshold, 1, 0)
    y_pred_3 = np.where(X_test > best_threshold_high_low, 2, y_pred)
    print(classification_report(y_test_3, y_pred_3, target_names=["Negative", "Low", "High"]))

    


