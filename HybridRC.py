
#!/usr/bin/env python

import math
import re
import sys
import csv
import numpy
from collections import defaultdict
import copy
import random
import time
import datetime



def calculateZScore():

    rows = list()  # List to take the rows from the csv file
    zscoreRating = list()

    with open('inputData.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            rows.append(row)

    # Loop to convert the items in the list to the right type
    for i in range(len(rows)):
        # only convert rating to float
        rows[i][2] = float(rows[i][2])

    i = 0
    # While loop to go through the contents of rows and create block of each user and find z score of that block
    while i < len(rows):
        tempUser = list()
        prevUser = rows[i][0]
        userrating = list()

        # While loop to go through the single user and add it to tempUser list
        while (rows[i][0] == prevUser):
            tempUser.append(rows[i])
            userrating.append(rows[i][2])
            i = i + 1
            if (i >= len(rows)):
                break

        # calculate zscore for this temp user
        mean = (sum(userrating)) / (len(userrating))
        standarddeviation = numpy.std(userrating)

        for j in range(len(tempUser)):
            zscore = (tempUser[j][2] - mean) / standarddeviation
            tempUser[j][2] = float("{0:.3f}".format(zscore))

        zscoreRating.append(tempUser)

    # add zscoreRating list to inputZScore.csv file
    with open('inputZScore.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile)
        for item in zscoreRating:
            writer.writerows(item)



def input(movieList,rows):
    #Read data from z score file
    with open('inputZScore.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            rows.append(row)

    #For loop to make the contect the right type
    for i in range(len(rows)):
        rows[i][0] = int(rows[i][0])
        rows[i][1] = int(rows[i][1])
        rows[i][2] = float(rows[i][2])
        rows[i][3] = int(rows[i][3])

    numUser=rows[len(rows)-1][0]

    for i in range(len(rows)):
        if(rows[i][0]==1):
            movieList.append(rows[i][1])
        elif(rows[i][0]!=1):
            break

    for i in range(len(rows)):
        l = True
        movie = rows[i][1]
        for k in range(len(movieList)):
            if (movie == movieList[k]):
                l = False
                break
        if (l == True):
            movieList.append(movie)

    return numUser

def insertrating(movierating, rows, numUser, lengthm, movieList):
    #For loop to initialize the wait list with 0
    for i in range(numUser):
        content = list()  # list to hold the values in each column of the row
        # For lop to go through the columns of each row
        for j in range(lengthm):
            c = -10
            content.append(c)
        movierating.append(content)
    rateValues(rows, movierating,movieList) #Function call to insert in the movie rating values

def rateValues(rows, movierating,movieList):
    #For loop to create the list of wait with the correct values for the user
    for i in range(len(rows)):
        a=rows[i][0]-1 #The user number
        b=movieList.index(rows[i][1])#The movie
        movierating[a][b]=rows[i][2]

def squareRootUsers(movierating,squsers):
    for i in range(len(movierating)):
        sum = 0
        for j in range(len(movierating[i])):
            sum=sum+(movierating[i][j] ** 2)

        powi=pow(sum,.5)
        squsers.append(powi)

def dotproduct(movierating,dpmatrix, numUser):

    for i in range(numUser):

        v = list()
        for j in range(numUser):
            sum=0
            for k in range(len(movierating[i])):
                if(movierating[i][k]==-10 or movierating[j][k] == -10):
                    prod=0
                else:
                    prod=movierating[i][k]*movierating[j][k]
                sum=sum+(prod)
            v.append(sum)
        dpmatrix.append(v)

def cossimcsv(movierating,squsers, dpmatrix):
    cossimcsv=list() #array to hold the cosine similarities values
    #For loop to go through the movierating list for user a
    for i in range (len(movierating)):
        # For loop to go through the movierating list for user b
        n=list()
        for j in range(len(movierating)):
            if (j==i):
                n.append(-1000)
            if(j!=i):
                c=list()
                pow=squsers[i]*squsers[j]
                if (pow == 0):
                    pow = 1
                cossim= (dpmatrix[i][j])/(pow)
                n.append(cossim)
        cossimcsv.append(n)


    with open('cossimilarity.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(cossimcsv)

def readingcsvfile(movieList, movierating,recommendations):

    rows = list()  # List to hold the rows
    mylist = list()
    #read data from  cosine similarity file
    with open('cossimilarity.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            rows.append(row)

    for i in range(len(rows)):
        for j in range(len(rows[i])):
            rows[i][j] = float(rows[i][j])

    #create user-movie rating matrix
    for i in range(len(rows)):
        usercompare = list()
        for j in range(len(rows[i])):
            c = list()
            user = j + 1
            c.append(user)
            c.append(rows[i][j])
            usercompare.append(c)
        usercompare = sorted(usercompare, key=lambda index: index[1], reverse=True)
        mylist.append(usercompare)

        #initializing all user rating to default -10
        for j in range(len(usercompare)):
            user = usercompare[j][0]
            arecommend = list()  # recommneded movies for a
            for k in range(len(movierating[i])):
                if movierating[i][k] == -10:
                    if movierating[user - 1][k] > 0:
                        temp = list()
                        movie = movieList[k]
                        temp.append(movie)
                        temp.append(movierating[user - 1][k])
                        arecommend.append(temp)

            if len(arecommend) > 0:
                arecommend = sorted(arecommend, key=lambda index: index[1], reverse=True)
                userused = user
                break

        cfSetSize=len(arecommend)

        if cfSetSize> 20:
            cfSetSize=20

        subtopCFMovies = list()
        for j in range(cfSetSize):
            subtopCFMovies.append(arecommend[j][0])

        addList=list()
        addList.append(i + 1)
        addList.append(subtopCFMovies)

        recommendations.append(addList)

    with open('readingcsvfile.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        writer.writerows(recommendations)

def actualCFSimilarity(movieList, movierating,oldMovieData):

    CFRecc=list()
    rows = list()  # List to hold the rows
    mylist = list()

    #read data from cosine similarity file
    with open('cossimilarity.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            rows.append(row)

    for i in range(len(rows)):
        for j in range(len(rows[i])):
            rows[i][j] = float(rows[i][j])

    for i in range(len(rows)):
        usercompare = list()
        #find most similar user
        for j in range(len(rows[i])):
            c = list()
            user = j + 1
            c.append(user)
            c.append(rows[i][j])
            usercompare.append(c)
        usercompare = sorted(usercompare, key=lambda index: index[1], reverse=True)
        mylist.append(usercompare)

        #get most similar user movie that user i hasn't seen yet
        for j in range(len(usercompare)):
            user = usercompare[j][0]
            arecommend = list()  # recommneded movies for a
            for k in range(len(movierating[i])):
                if movierating[i][k] == -10:
                    if movierating[user - 1][k] > 0:
                        temp = list()
                        movie = movieList[k]
                        temp.append(movie)
                        temp.append(movierating[user - 1][k])
                        arecommend.append(temp)

            if len(arecommend) > 0:
                break

        addList=list()
        addList.append(i + 1)
        addList.append(arecommend[0][0])

        CFRecc.append(addList)

    expectedOutputRows=list()
    with open('expectedOutput.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            expectedOutputRows.append(row)

    for i in range(len(expectedOutputRows)):
        expectedOutputRows[i][1]=int(expectedOutputRows[i][1])

    oldMovieIDList=list()
    for i in range(len(oldMovieData)):
        oldMovieIDList.append(oldMovieData[i][0])

    listFinalExpect=list()

    #compare CF recommendaded movie to user preffered movie
    for i in range(len(CFRecc)):
        movieIDExpect=str(expectedOutputRows[i][1])

        movieIDFinal=str(CFRecc[i][1])
        currentMovieIndex=oldMovieIDList.index(movieIDFinal)
        movieExpectedIndex=oldMovieIDList.index(movieIDExpect)

        movieFinalGenre = list(oldMovieData[currentMovieIndex][1])
        movieExpectGenre = list(oldMovieData[movieExpectedIndex][1])

        intersectionSet = list(set(movieFinalGenre) & set(movieExpectGenre))
        unionSet = list(set(movieFinalGenre) | set(movieExpectGenre))

        finalExpectSim=float(len(intersectionSet)) / float(len(unionSet))

        listAdded=list()
        listAdded.append(i+1)
        listAdded.append(finalExpectSim)

        listFinalExpect.append(listAdded)


    with open('ActualCFRecc.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        writer.writerows(listFinalExpect)



def readMovieFile(oldMovieData):

    rows=list()
    #read movie data from movies file
    with open('movies.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            rows.append(row)

    rows.pop(0)

    #store movie data in oldMovieData
    for i in range(len(rows)):
        temp_movie=list()
        temp_movie.append(rows[i][0])
        temp_movie.append(rows[i][2].split("|"))
        oldMovieData.append(temp_movie)

def createClusterModel(k,movieData,oldMovieData):

    randomk=list()
    keyList=list()
    valueList=list()
    newValueList = list()

    last=len(oldMovieData)-1
    i = 0
    #To select initial cluster centroid random
    while(i<k):
        temprandom = random.randint(0, last)
        if temprandom not in randomk:
            randomk.append(temprandom)
            i=i+1

    #For loop to add the genre of the centroid to the keyList
    for i in range(len(randomk)):
        genre=list(oldMovieData[randomk[i]][1])
        keyList.append(genre)

    #initialize initial cluster (only one point)
    for i in range(len(keyList)):
        l = list()
        valueList.append(l)

    for i in range(len(keyList)):

        tempList=list()
        subtemp = list()

        tempList.append(oldMovieData[randomk[i]][0])
        tempList.append(list(oldMovieData[randomk[i]][1]))

        subtemp.append(i)
        subtemp.append(int(oldMovieData[randomk[i]][0]))
        tempGenre = list(oldMovieData[randomk[i]][1])
        movieGenre = ",".join(tempGenre)
        subtemp.append(movieGenre)
        newValueList.append(subtemp)

        valueList[i].append(tempList)


    for i in range(len(oldMovieData)):
        if i not in randomk:
            movieData.append(oldMovieData[i])

    demodistance=list()

    #For loop to find the distance for movie i to all the other clusters
    for i in range(len(movieData)):
        distanceList=list()
        currentGenre=list(movieData[i][1])
        subNewValue = list()

        #For loop to get the distance from movie i to cluster j
        for j in range(len(keyList)):
            #print keyList[j]
            clusterGenre=list(keyList[j])
            tempDistance=list()

            intersectionSet=list(set(clusterGenre) & set(currentGenre))
            unionSet = list(set(clusterGenre) | set(currentGenre))
            jaccardDistance=1.0-(float(len(intersectionSet))/float(len(unionSet)))

            tempDistance.append(j)
            tempDistance.append(jaccardDistance)

            distanceList.append(tempDistance)

        distanceList = sorted(distanceList, key=lambda index: index[1], reverse=False)

        demodistance.append(distanceList)

        smallDistance=list(distanceList[0])

        clusterID= smallDistance[0]

        valueList[clusterID].append(movieData[i])


        subClusterList=list()

        for point1 in range(len(valueList[clusterID])):

            subpoint=list()
            tempDist=list()
            point1genre= list(valueList[clusterID][point1][1])

            for point2 in range(len(valueList[clusterID])):

                point2genre = list(valueList[clusterID][point2][1])
                intersectionSet1 = list(set(point2genre) & set(point1genre))
                unionSet1 = list(set(point2genre) | set(point1genre))
                jaccardDistance1 = 1.0 - (float(len(intersectionSet1)) / float(len(unionSet1)))
                tempDist.append(jaccardDistance1)

            tempDist = sorted(tempDist,reverse=True)
            highDist= tempDist[0]
            subpoint.append(point1genre)
            subpoint.append(highDist)

            subClusterList.append(subpoint)

        subNewValue.append(clusterID)
        subNewValue.append(int(movieData[i][0]))
        tempGenre=list(movieData[i][1])
        movieGenre=",".join(tempGenre)
        subNewValue.append(movieGenre)

        newValueList.append(subNewValue)

        subClusterList = sorted(subClusterList, key=lambda index: index[1], reverse=False)

        newClusteroid=subClusterList[0][0]

        keyList[clusterID]=newClusteroid

    newValueList = sorted(newValueList, key=lambda index: index[1], reverse=False)

    with open('kmeansclustermodel_100.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        writer.writerows(newValueList)

def findUserCluster(k):
    movieList1 = list()
    movieClusterList = list()

    rows = list()
    #Read cluster model file
    with open('kmeansclustermodel_100.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            rows.append(row)

    #Convert data to proper type
    for i in range(len(rows)):
        tempMovie = list()
        tempList = list(rows[i][2].split(","))

        tempMovieID = rows[i][1]
        tempMovie.append(rows[i][0])
        tempMovie.append(tempMovieID)
        tempMovie.append(tempList)

        movieClusterList.append(tempMovie)
        movieList1.append(tempMovieID)

    ZScoreRows = list()
    #Read z score file
    with open('inputZScore.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            ZScoreRows.append(row)

    userDataList = list()

    #Convert z score to proper type
    for i in range(len(ZScoreRows)):
        tempUserList = list()

        tempUserList.append(ZScoreRows[i][0])
        tempUserList.append(ZScoreRows[i][1])
        zrating = float(ZScoreRows[i][2])
        tempUserList.append(zrating)

        userDataList.append(tempUserList)

    userCluster = list()
    userDataPerBlockList = list()
    i = 0
    DemoList = list()
    majorTemp = list()
    while (i < len(userDataList)):
        temp = list()
        currUser = int(userDataList[i][0])

        userBlock = list()
        #Getting user history movie block
        while (currUser == int(userDataList[i][0])):
            userBlock.append(userDataList[i])
            i = i + 1
            if (i >= len(userDataList)):
                break

        userDataPerBlockList.append(userBlock)

        clusterAvgRating = list()
        for j in range(k):
            tempList = list()

            tempList.append(j)
            tempList.append(0.0)
            tempList.append(0.0)

            clusterAvgRating.append(tempList)


        for j in range(len(userBlock)):
            index_m = int(movieList1.index(userBlock[j][1]))
            cluster_m = int(movieClusterList[index_m][0])
            clusterAvgRating[cluster_m][1] += float(userBlock[j][2])
            clusterAvgRating[cluster_m][2] += 1.0

            subtemp = list()
            subtemp.append(currUser)
            subtemp.append(userBlock[j][1])
            subtemp.append(userBlock[j][2])
            subtemp.append(cluster_m)
            temp.append(subtemp)

        majorTemp.append(temp)

        finalRatingList = list()
        subDemoList = list()
        for j in range(len(clusterAvgRating)):
            tempAvgList = list()
            tempAvgList.append(clusterAvgRating[j][0])

            if (clusterAvgRating[j][2] <= 0):
                tempAvgList.append(0.0)
                avgrating = 0.0

            else:
                avgrating = float(clusterAvgRating[j][1]) / float(clusterAvgRating[j][2])
                tempAvgList.append(avgrating)

            finalRatingList.append(tempAvgList)
            subDemoList.append(currUser)
            subDemoList.append(j)
            subDemoList.append(avgrating)
            DemoList.append(subDemoList)

        finalRatingList = sorted(finalRatingList, key=lambda index: index[1], reverse=True)

        userClusterID = finalRatingList[0][0]

        #pick highest rated movie from higest avg rated cluster
        itemHighestRating = -10.0
        itemHighestMovieId = ' '
        for j in range(len(temp)):
            blockItemCluster = temp[j][3]
            blockItemRating = float(temp[j][3])

            if(blockItemCluster==userClusterID and blockItemRating>itemHighestRating):
                itemHighestRating = blockItemRating
                itemHighestMovieId = temp[j][1]


        tempUserCluster = list()

        tempUserCluster.append(currUser)
        tempUserCluster.append(userClusterID)
        tempUserCluster.append(itemHighestMovieId)

        userCluster.append(tempUserCluster)

    with open('userCluster.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        writer.writerows(userCluster)

def findUserKMeansSet(topKMeansMovies):

    userClusterrows=list()
    #Read from user cluster file
    with open('userCluster.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            userClusterrows.append(row)

    kmeansMovieList=list()
    #Read from cluster model file
    with open('kmeansclustermodel_100.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            kmeansMovieList.append(row)

    for i in range(len(userClusterrows)):
        userClusterID=userClusterrows[i][1]
        userHighestMovieID = userClusterrows[i][2]

        clusterMovieList=list()
        for j in range(len(kmeansMovieList)):

            if kmeansMovieList[j][0]== userClusterID:

                if kmeansMovieList[j][1] == userHighestMovieID:
                    sourceGenre=list(kmeansMovieList[j][2])
                else:
                    tempClusterMovieList=list()
                    tempClusterMovieList.append(kmeansMovieList[j][1])
                    tempClusterMovieList.append(list(kmeansMovieList[j][2]))
                    clusterMovieList.append(tempClusterMovieList)

        distanceList=list()

        for j in range(len(clusterMovieList)):
            tempDistList=list()

            intersectionSet=list(set(sourceGenre) & set(clusterMovieList[j][1]))
            unionSet = list(set(sourceGenre) | set(clusterMovieList[j][1]))
            jaccardDistance=1.0-(float(len(intersectionSet))/float(len(unionSet)))

            tempDistList.append(clusterMovieList[j][0])
            tempDistList.append(jaccardDistance)

            distanceList.append(tempDistList)

        distanceList = sorted(distanceList, key=lambda index: index[1], reverse=False)

        setSize=len(distanceList)

        if setSize> 20:
            setSize=20

        subtopKMeansMovies = list()
        for j in range(setSize):
            subtopKMeansMovies.append(int(distanceList[j][0]))

        addList=list()
        addList.append(userClusterrows[i][0])
        addList.append(subtopKMeansMovies)
        topKMeansMovies.append(addList)

    with open('topKMeansMovies.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        writer.writerows(topKMeansMovies)

def finalResultDetermine(recommendations, topKMeansMovies, finalResult):


    for i in range(len(recommendations)):
        temfinalResult=list()

        intersectionSet = list(set(recommendations[i][1]) & set(topKMeansMovies[i][1]))

        if (len(intersectionSet)==0):
            if (len(recommendations[i][1])>0) and (len(topKMeansMovies[i][1]) > 0):
                intersectionSet.append(topKMeansMovies[i][1][0])
                if len(topKMeansMovies[i][1])>1:
                    intersectionSet.append(topKMeansMovies[i][1][1])
                intersectionSet.append(recommendations[i][1][0])
                if len(recommendations[i][1]) > 1:
                    intersectionSet.append(recommendations[i][1][1])

            elif (len(recommendations[i][1])==0) and (len(topKMeansMovies[i][1]) > 0):
                intersectionSet.append(topKMeansMovies[i][1][0])
                if len(topKMeansMovies[i][1]) > 1:
                    intersectionSet.append(topKMeansMovies[i][1][1])
            elif (len(recommendations[i][1])>0) and (len(topKMeansMovies[i][1]) == 0):
                intersectionSet.append(recommendations[i][1][0])
                if len(recommendations[i][1]) > 1:
                    intersectionSet.append(recommendations[i][1][1])

        temfinalResult.append(recommendations[i][0])
        temfinalResult.append(intersectionSet)
        finalResult.append(temfinalResult)


def determineSimilarityFinalExpected(finalResult,oldMovieData):

    expectedOutputRows=list()
    oldMovieIDList=list()

    with open('expectedOutput.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            expectedOutputRows.append(row)

    for i in range(len(expectedOutputRows)):
        expectedOutputRows[i][1]=int(expectedOutputRows[i][1])

    for i in range(len(oldMovieData)):
        oldMovieIDList.append(oldMovieData[i][0])

    listFinalExpect=list()
    for i in range(len(finalResult)):
        numMoviesFinalResult=len(finalResult[i][1])
        movieIDExpect=str(expectedOutputRows[i][1])

        tempListFinalExpect = list()
        for j in range(numMoviesFinalResult):

            movieIDFinal=str(finalResult[i][1][j])

            currentMovieIndex=oldMovieIDList.index(movieIDFinal)
            movieExpectedIndex=oldMovieIDList.index(movieIDExpect)

            movieFinalGenre = list(oldMovieData[currentMovieIndex][1])
            movieExpectGenre = list(oldMovieData[movieExpectedIndex][1])

            intersectionSet = list(set(movieFinalGenre) & set(movieExpectGenre))
            unionSet = list(set(movieFinalGenre) | set(movieExpectGenre))

            finalExpectSim=float(len(intersectionSet)) / float(len(unionSet))

            tempListFinalExpect.append(finalExpectSim)

        tempListFinalExpect = sorted(tempListFinalExpect, reverse=True)

        listAdded=list()
        listAdded.append(i+1)
        listAdded.append(tempListFinalExpect[0])

        listFinalExpect.append(listAdded)

    with open('finalResult100.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        writer.writerows(listFinalExpect)

if __name__ == '__main__':

    print("hello from hybrid new")

    rows=list()
    userInput=list()
    movies=list() #All the movies seen by an individual user
    movieList=list() #Array to hold the movies seen by all the users
    movierating=list() #Array to hold how the users ratedthe movie
    squsers=list() #array to hold the squaretoor values
    dpmatrix=list()
    recommendations=list()

    calculateZScore()

    print("Function input started\n")
    numUser=input(movieList,rows)
    movieList = sorted(movieList)
    lengthm=len(movieList)

    print("Function movierating started\n")
    insertrating(movierating, rows, numUser, lengthm, movieList)

    print("Function square root started\n")
    squareRootUsers(movierating, squsers)

    print("Function dot product started\n")
    dotproduct(movierating, dpmatrix, numUser)


    print("Function cosine sim started\n")
    cossimcsv(movierating, squsers, dpmatrix)

    print("Function reading csv started\n")
    readingcsvfile(movieList, movierating,recommendations)


    oldMovieData = list()
    movieData = list()
    topKMeansMovies = list()
    finalResult = list()
    k = 100

    print("Function readMovieFile started\n")
    readMovieFile(oldMovieData)
    actualCFSimilarity(movieList, movierating,oldMovieData)

    print("Function createClusterModel started\n")
    createClusterModel(k,movieData,oldMovieData)

    print("Function findUserCluster started\n")
    findUserCluster(k)

    print("Function findUserKMeansSet started\n")
    findUserKMeansSet(topKMeansMovies)


    print("Function finalResultDetermine started\n")
    finalResultDetermine(recommendations, topKMeansMovies,finalResult)

    print("Function determineSimilarityFinalExpected started\n")
    determineSimilarityFinalExpected(finalResult, oldMovieData)

    





