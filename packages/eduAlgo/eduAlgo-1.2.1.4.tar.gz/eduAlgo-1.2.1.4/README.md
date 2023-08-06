<img src ="https://edualgo.github.io/documentation/assets/images/eduAlgo.png" height = "250">

# eduAlgo

<img src="https://img.shields.io/github/license/Abhijit2505/eduAlgo?style=for-the-badge">&nbsp;<img src ="https://img.shields.io/github/languages/code-size/Abhijit2505/eduAlgo?style=for-the-badge">&nbsp;<img src = "https://img.shields.io/github/contributors/Abhijit2505/eduAlgo?style=for-the-badge">&nbsp;<img src ="https://img.shields.io/github/last-commit/Abhijit2505/eduAlgo?style=for-the-badge">&nbsp;<img src="https://img.shields.io/pypi/wheel/eduAlgo?style=for-the-badge">

<img src = "https://img.shields.io/pypi/status/eduAlgo?style=for-the-badge">&nbsp;<img src ="https://img.shields.io/pypi/v/eduAlgo?style=for-the-badge&logo=PyPi">&nbsp;<img src ="https://img.shields.io/github/release-date/Abhijit2505/eduAlgo?style=for-the-badge">


[![forthebadge](https://forthebadge.com/images/badges/built-with-love.svg)](https://forthebadge.com)   [![forthebadge](https://forthebadge.com/images/badges/built-by-developers.svg)](https://forthebadge.com) [![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://forthebadge.com)

## Objective
A python package published at [PyPi](https://pypi.org/). The project can be viewed here => [PyPi - eduAlgo](https://pypi.org/project/eduAlgo/).

## Aim Of The Package

This is a very simple python package made up with python script to study different algorithms for educational purposes. This package is currently under **planning** version and aims to achieve the following :-

* To put together all the available algorithms
* Help students with learning space and time complexity
* Visualizing Algorithms
* Getting resources, articles etc. to study about python and Algorithms
* Become a handy tool for the programmers while using different algorithms on daily basis

## Organization

This project is a part of the organization <a href="https://edualgo.github.io/organization/">eduAlgo</a>.

> We are an opensource organization having a few open-sourced projects on github related to Data structures and Algorithms in Python, Flutter Development & Frontend Development.
chek the organization here - <a href="https://github.com/eduAlgo">eduAlgo</a>

## Documentation
The documentation for the included methods and their implementations can be found here => <a href = "https://edualgo.github.io/documentation/index.html">eduAlgo-Documentation</a>

## Algorithms Yet to Publish

* Searching Algorithms and Visualizations
* Sorting Algorithms and Visualizations
* Graph Algorithms and Visualizations
* Linked List Implementations and Vizualizations
* Tree Types, Vizualizations and Implementations

## Installation

Fast install:

    pip install eduAlgo

Example

```python

from edualgo import LinkedList as ll
llist1 = ll.linkedlist()
llist2 = ll.linkedlist()

arr1 = list(map(int,input().split()))
arr2 = list(map(int,input().split()))

for i in arr1:
    llist1.append(i)

for i in arr2:
    llist2.append(i)

sol = ll.list_algorithms()

llist3 = ll.linkedlist()
llist3.head = sol.mergeTwoLists(llist1.head,llist2.head)
llist3.printLL()
```
Input:

      1 2 3
      2 3 4

Output:

      1 2 2 3 3 4

