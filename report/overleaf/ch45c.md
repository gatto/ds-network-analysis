For the communities formed, we initially tried to ascertain whether communities had been created in which users belonging to only one category were present, but this was not the case. For the most part each community found presents an equal distribution of the four types of users identified. Only in very small communities are there at most two types of users. Therefore, the communities formed do not represent communities of opinion, at least according to our opinion categorization.
Subsequently we investigated the existence of patterns in terms of geolocation in the formation of communities through the localisation of each individual tweet and therefore their user. We could not find a common geographical location in the larger communities but we could find this geographical pattern in some of the smaller communities. Specifically we found retweet communities of Italian users or users between Russia and Ukraine.
In regards to this last investigation, we highlight a limitation in the presence of null values in the geolocations of many tweets. Also, some users used fictitious or overgeneralized locations (e.g. “World”) and could not be included in the analysis.

## Task: Opinion dynamics
In this phase of our analysis we focused on how the opinions/positions of users in our network can change following the active diffusion models of Opinion Dynamics.
In particular, we implemented *Voter*, *Majority rule* and *Sznajd* models. We applied these diffusion models to our network and then compared them with the results obtained on the Barabasi-Albert and Watts-Strogatz synthetic networks.
With the application of these models we analyze the trend of the diffusion of an opinion, inserted within a network, which can take only 2 possible values: +1 (positive opinion) or -1 (negative opinion), which can be displayed in our graphs respectively with the colors orange ("infected") and blue ("susceptible").
Our analysis for all 3 models starts from the hypothesis of an initial balancing situation between "infected" and "susceptible" and a number of iterations equal to 2000.
### Voter model
The Voter model applied to our network shows a divergent trend between the two opinions, even before the 250th iteration. In this case, nodes with positive opinion tend to increase with increasing iterations, and the number of nodes with negative opinion tends to decrease more and more.
This result can be compared to the trend of the same model applied to a synthetic network of the Watts-Strogatz type with similar characteristics: in fact, even in this case, even if only after the 500th iteration, the model shows this type of divergent trend between the two opinions. However, while noting divergence, the trend of opinions is opposite: the nodes with positive opinion decrease over time.

xxx 2 voter models

a) Voter model on Real Network 
b) Voter model on Watts-Strogatz 

### Majority rule model
On our network the diffusion model shows a very rapid trend reversal: in fact, in the first iterations the "positive" nodes are higher than the "negative" ones, while starting from the 30th iteration we see the positive ones decrease and the negatives increase.
We find a similar trend on the Barabasi-Albert: even here, in fact, the nodes with positive opinion are greater than the negatives but unlike what we saw on our network here the trend reversal takes place much later, starting from the 1000th iteration.

xxx 2 majority models

a) Majority rule on G
b) Majority rule on BA 

### Sznajd model
In our network the trend of the two opinions tends to stabilize around the 750th iteration with a prevalence of the negative opinion. 

xxx sznajd 1
 
a) Sznajd model on G 
 
In synthetic models, however, opinions tend to diverge and one of the two tends to disappear, with a clear dominance of negative opinion observable especially on Barabasi-Albert.

xxx sznajd 2

b) Sznajd model on BA

In Watts-Strogatz, the dominance of negative opinion undergoes a reversal around the 250th iteration and then reverses again around the 500th iteration, then finally asserts itself as the dominant opinion.

xxx sznajd 3

c) Sznajd model on WS
