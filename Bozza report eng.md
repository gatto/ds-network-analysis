# SNA PROJECT
Our analysis aims to build a network inspired by the spread of debate (tweets and retweets) about the outbreak of the conflict in Ukraine. 
We started to analyze tweets in English from February 24, 2022 to May 20(?). 
The idea was to try to classify users' tweets into 4 groups: 

     •	Pro Ucraina 
     •	Pro Russia
     •	"Pax Romana 
     •	"I don’t care" 

The goal is to categorize users by examining their tweets. 

The analysis we will perform on the tweets will involve not only observing the hashtags in them, but also analyzing the trend of the tweets with the ultimate goal of going out and identifying those that could be potential bots within the network. 

## TWARK

Through the Twark library, we implemented several functions that allowed us to perform our search of various tweets:

- SocialETL, allows us to extract with the use of a query a given keyword
- Count, allows us to identify how often a given keyword appears on Twitter
- Hashtags, allows us to extract hashtags from tweets


 All these functions are considered within a time range from February 24 onward.


## 1 CAT TREE 
How do we identify sets of hashtags to categorize various users based on the tweets they post? 
The "cat tree method" consists of:
- create a list for each category  
- identify a "parent" hashtag for each category, which will be placed in the list belonging to it 
- select the children of each parent, which will be placed in the belonging list


### 1.1. (parent)Hashtags
In our case we identified 3 main categories with the following parent hastags:

     (a) Pro Ukraine - #slavaukraini  

     b) Pro Russia - #istandwithputin

     c) Pax Romana - #stopwarinukraine

The parent hashtags were selected using the Count function,through which we searched for the most frequently used hashtags in the tweets.
For each category we identified possible candidates through searches on major social networks and through search engines.

To idetify the "parent" hashtag for each category through the Count function we selected the most "tweeted" one.




| Pro Ucraina | count | Pro Russia | count | Pax Romana | count |
| ---- | ---- | ---- | ---- | ---- | ---- |       
| #slavaukraini | 871114 | #istandwithputin | 259662  | #stoprussia | 1887070 |
|#IStandWithUkraine  | 633918  | #istandwithrussia | 153669  | #stopwarinukraine | 250781 |


Regarding the PaxRomana category, although the candidate hashtag #stoprussia reached a larger number of tweets, we decided to choose the hashtag #stopwarinukraine as it seemed to us semantically more akin to the line of thinking of the category it is going to represent. 

Infact the  #stopoprussia hashtag seemed too "pro-Ukrainian" to represent the PaxRoman category.


### 1.2. Hashtags- figli
After identifying the parent relative to each category, we searched for all tweets containing such parent hashtags (#slavaukraini, #istandwithputin, #stopwarinukraine), and if a tweet included a parent hashtag + other hashtags, these hashtags were automatically included in the parent's belonging list.
(give example).
After sorting the lists by the number of times they appeared(first=most tweeted), the next steps would consist of:
(a) apply a first score to eliminate hashtags that appear in more than one list. 
(b) repeat the needle for the first k children of each list (k=3), so as to find hashtags from not only the parent one.
(c) reapplying the score on the final lists
(d) list cleaning 
(e) identify a metedo to select a fourth category: I don't care category. 




### 1.3. Duplicate removing
A first problem encountered ( point (a) and point (c) ) was that a child could appear in more than one list, thus not having a well-defined categorization. To solve this, we decided to assign a score to each child that is present in more than one list.

Score-cat-method: 
A second search is performed for each child belonging to more than one category fj: 
- search for all (recent?) tweets that contain the repeated child + the 3 parent hashtags and save them in 3 different lists
- do the count of the total number of tweets (child + each parent hashtags) found: c_tot= Σ i=1 There
- do the count of the number of times the child appears together with a given parent hashag, for each category i: Ci
The score for each repeated child fj is given by:  Ci / Σ i=1 Ci
We assign a repeated child fj to a given category if: 
- score>threshold
- if score>threshold


### 1.4 List cleaning 
After creating an algorithm to automatically eliminate duplicates, a human (arbitrary) assessment must be made as to whether or not a hashtag belongs to a particular category.
For example, among the various hashtags that emerged, #russia or #Ukraine appear several times. These do not belong to any category as we felt that they were too generic and uncharacteristic words to fit into one of the 3 categories, so they were removed from the lists.

Next, we decided to remove hashtags irrelevant for categorization purposes, such as all hashtags with only one count or with a count less than a certain thershold (e.g., 0.1% ).
We defined the threshold_support parameter with the function of going to consider only hashtags that appear in at least 0.1% of the tweets.

### 1.5. Identifying 4 category: "I don’t care"
The remaining category, called "I don't care," aims to collect tweets from users who are disinterested in the topic. 

Unfortunately, the approach used above cannot be used for this fourth category ("I dont care"), as it was not possible to identify an actual hashtag representing this line of thinking.
We therefore opted for a "by exclusion" selection mechanism: we look at hashtags used by people who tweeted about focuses other than war, e.g., the Eurovision contest, by simply using the hashtag #eurovision on the tweet search query.
We will focus only on "active" users on the platform.
The users we are going to consider as vcandidates for the 4 category can already be considered as active users as we are only considering tweets in our period of interest (February 24-present) and as they are users who have used popular hashtags in the last period.

  If the most active users identified did not use one of the hashtags belonging to one of the 3 groups already identified, we will classify these users in the "I don't care" category. 

------------ da correggere---------------------------------------------------------------------------------

   -To identify the most active users we use the attribute ['author.public_metrics.tweet_count']

   -In contrast, to identify the hastags used by a user, we will consider the attribute ['author.entities.description.hashtags']





