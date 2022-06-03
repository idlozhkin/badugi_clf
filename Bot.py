from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score, recall_score


def prediction1(win_prob, dro, answer, turn, count_change):
    if turn == 0:
        if dro >= 3 or (dro == 2 and win_prob > 0.15):
            return 1
        if answer == 0:
            return 0
        if count_change > 0 and dro == 2 and win_prob > 0.11:
            return 1
        return 0
    if turn == 1:
        if dro == 4 or (dro == 3 and win_prob > 0.7):
            return 1
        if answer == 0:
            return 0
        if dro == 3 and win_prob > 0.64 and count_change > 1:
            return 1
        return 0
    if turn == 2:
        if dro == 4 or (dro == 3 and win_prob > 0.85):
            return 1
        if answer == 0:
            return 0
        if dro == 3 and win_prob > 0.74 and count_change == 0:
            return 1
        return 0


def prediction2(win_prob, dro, answer, turn, count_change):
    if turn == 0:
        if dro >= 3 or (dro == 2 and win_prob > 0.3):
            return 1
        if answer == 0:
            return 0
        if dro == 2 and win_prob > 0.2:
            return 1
        return 0
    if turn == 1:
        if dro == 4 or (dro == 3 and win_prob > 0.5):
            return 1
        if answer == 0:
            return 0
        if dro == 3 and win_prob > 0.36:
            return 1
        return 0
    if turn == 2:
        if dro == 4 or (dro == 3 and win_prob > 0.9):
            return 1
        if answer == 0:
            return 0
        if dro == 3 and win_prob > 0.85:
            return 1
        return 0


def upgrade_clf(poker_data, finished_learn):
    X = poker_data.drop(['choose'], axis=1)
    y = poker_data.choose

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    clf_rf = RandomForestClassifier()
    parameters = {'n_estimators': [10, 15], 'criterion': ['gini', 'entropy'], 'max_depth': range(1, 10)}
    grid_search_cv_clf = GridSearchCV(clf_rf, parameters, cv=5)
    grid_search_cv_clf.fit(X_train, y_train)
    best_clf_rf = grid_search_cv_clf.best_estimator_

    y_pred = best_clf_rf.predict(X_test)
    if precision_score(y_test, y_pred) > 0.8 and recall_score(y_test, y_pred) > 0.8:
        finished_learn[0] = True

    return best_clf_rf
