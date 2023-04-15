## Network characterization

We will start with the analysis of the basic measures of our network while comparing them with those obtained on 3 synthethic nets: Erdos-Renyi, Barabasi-Albert and Watts-Strogatz.

Following the previous data cleaning phase, for the purposes of our analysis we decided to focus only on the giant component present. Again, nodes represent Twitter's users and links represent the presence of an interaction between the two users, which in our case is the Twitter *mention*. Our network is *undirected* (we considered the interaction between 2 users as reciprocal) and *unweighted*.

We used `networkX` to model our network as a Real-World Network (also named "RW"). Then we used *Gephi* to assign a different color to each node based on its category.

For an initial visualization we used the *Force Atlas 2* layout to try and give a general although clear idea of the structure of the network (see figures).
