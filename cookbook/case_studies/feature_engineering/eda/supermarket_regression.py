"""
Supermarket Regression Notebook
===============================

"""

import matplotlib.pyplot as plt
import numpy as np

# reference: https://github.com/risenW/medium_tutorial_notebooks/blob/master/supermarket_regression.ipynb
import pandas as pd
import seaborn as sns

# makes graph display in notebook
# %matplotlib inline

supermarket_data = pd.read_csv(
    "https://raw.githubusercontent.com/risenW/medium_tutorial_notebooks/master/train.csv"
)

supermarket_data.head()

supermarket_data.describe()

# remove ID columns
cols_2_remove = [
    "Product_Identifier",
    "Supermarket_Identifier",
    "Product_Supermarket_Identifier",
]

newdata = supermarket_data.drop(cols_2_remove, axis=1)

newdata.head()

cat_cols = [
    "Product_Fat_Content",
    "Product_Type",
    "Supermarket _Size",
    "Supermarket_Location_Type",
    "Supermarket_Type",
]

num_cols = [
    "Product_Weight",
    "Product_Shelf_Visibility",
    "Product_Price",
    "Supermarket_Opening_Year",
    "Product_Supermarket_Sales",
]

# bar plot for categorial features
for col in cat_cols:
    fig = plt.figure(figsize=(6, 6))  # define plot area
    ax = fig.gca()  # define axis

    counts = newdata[col].value_counts()  # find the counts for each unique category
    counts.plot.bar(ax=ax)  # use the plot.bar method on the counts data frame
    ax.set_title("Bar plot for " + col)

# scatter plot for numerical features
for col in num_cols:
    fig = plt.figure(figsize=(6, 6))  # define plot area
    ax = fig.gca()  # define axis

    newdata.plot.scatter(x=col, y="Product_Supermarket_Sales", ax=ax)


# box plot for categorial features
for col in cat_cols:
    sns.boxplot(x=col, y="Product_Supermarket_Sales", data=newdata)
    plt.xlabel(col)
    plt.ylabel("Product Supermarket Sales")
    plt.show()

# correlation matrix
corrmat = newdata.corr()
f, ax = plt.subplots(figsize=(5, 4))
sns.heatmap(corrmat, square=True)

# pair plot of columns without missing values
import warnings

warnings.filterwarnings("ignore")

cat_cols_pair = ["Product_Fat_Content", "Product_Type", "Supermarket_Location_Type"]

cols_2_pair = [
    "Product_Fat_Content",
    "Product_Shelf_Visibility",
    "Product_Type",
    "Product_Price",
    "Supermarket_Opening_Year",
    "Supermarket_Location_Type",
    "Supermarket_Type",
    "Product_Supermarket_Sales",
]

for col in cat_cols_pair:
    sns.set()
    plt.figure()
    sns.pairplot(data=newdata[cols_2_pair], height=3.0, hue=col)
    plt.show()

# FEATURE ENGINEERING
# print all unique values
newdata["Product_Fat_Content"].unique()

fat_content_dict = {"Low Fat": 0, "Ultra Low fat": 0, "Normal Fat": 1}
newdata["is_normal_fat"] = newdata["Product_Fat_Content"].map(fat_content_dict)

# preview the values
newdata["is_normal_fat"].value_counts()

# assign year 2000 and above as 1, 1996 and below as 0
def cluster_open_year(year):
    if year <= 1996:
        return 0
    else:
        return 1


newdata["open_in_the_2000s"] = newdata["Supermarket_Opening_Year"].apply(
    cluster_open_year
)

# preview feature
newdata[["Supermarket_Opening_Year", "open_in_the_2000s"]].head(4)

# get the unique categories in the column as a list
prod_type_cats = list(newdata["Product_Type"].unique())

# remove the class 1 categories
prod_type_cats.remove("Health and Hygiene")
prod_type_cats.remove("Household")
prod_type_cats.remove("Others")


def cluster_prod_type(product):
    if product in prod_type_cats:
        return 0
    else:
        return 1


newdata["Product_type_cluster"] = newdata["Product_Type"].apply(cluster_prod_type)

newdata[["Product_Type", "Product_type_cluster"]].tail(10)

# transforming skewed features
fig, ax = plt.subplots(1, 2)

# plot of normal Product_Supermarket_Sales on the first axis
sns.histplot(data=newdata["Product_Supermarket_Sales"], bins=15, ax=ax[0])

# transform the Product_Supermarket_Sales and plot on the second axis
newdata["Product_Supermarket_Sales"] = np.log1p(newdata["Product_Supermarket_Sales"])
sns.histplot(data=newdata["Product_Supermarket_Sales"], bins=15, ax=ax[1])

plt.tight_layout()
plt.title("Transformation of Product_Supermarket_Sales feature")

# next, let's transform Product_Shelf_Visibility
fig, ax = plt.subplots(1, 2)

# plot of normal Product_Supermarket_Sales on the first axis
sns.histplot(data=newdata["Product_Shelf_Visibility"], bins=15, ax=ax[0])

# transform the Product_Supermarket_Sales and plot on the second axis
newdata["Product_Shelf_Visibility"] = np.log1p(newdata["Product_Shelf_Visibility"])
sns.histplot(data=newdata["Product_Shelf_Visibility"], bins=15, ax=ax[1])

plt.tight_layout()
plt.title("Transformation of Product_Shelf_Visibility feature")

# feature encoding
for col in cat_cols:
    print("Value Count for", col)
    print(newdata[col].value_counts())
    print("---------------------------")

# save the target value to a new variable
y_target = newdata["Product_Supermarket_Sales"]
newdata.drop(["Product_Supermarket_Sales"], axis=1, inplace=True)

# one hot encode using pandas dummy() function
dummified_data = pd.get_dummies(newdata)
dummified_data.head()

# fill-in missing values
# print null columns
dummified_data.isnull().sum()

# compute the mean
mean_pw = dummified_data["Product_Weight"].mean()

# fill the missing values with calculated mean
dummified_data["Product_Weight"].fillna(mean_pw, inplace=True)

# check if filling is successful
dummified_data.isnull().sum()

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    dummified_data, y_target, test_size=0.3
)

print("Training data is", X_train.shape)
print("Training target is", y_train.shape)
print("test data is", X_test.shape)
print("test target is", y_test.shape)

from sklearn.preprocessing import RobustScaler, StandardScaler

scaler = RobustScaler()

scaler.fit(X_train)

X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)

X_train[:5, :5]

from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import KFold, cross_val_score


def cross_validate(model, nfolds, feats, targets):
    score = -1 * (
        cross_val_score(
            model, feats, targets, cv=nfolds, scoring="neg_mean_absolute_error"
        )
    )
    return np.mean(score)


n_estimators = 150
max_depth = 3
max_features = "sqrt"
min_samples_split = 4
random_state = 2

from sklearn.ensemble import GradientBoostingRegressor

gb_model = GradientBoostingRegressor(
    n_estimators=n_estimators,
    max_depth=max_depth,
    max_features=max_features,
    min_samples_split=min_samples_split,
    random_state=random_state,
)

mae_score = cross_validate(gb_model, 10, X_train, y_train)
print("MAE Score: ", mae_score)

from flytekitplugins.papermill import record_outputs

record_outputs(mae_score=mae_score)