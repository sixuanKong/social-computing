import pandas as pd
import networkx as nx

from warnings import simplefilter

simplefilter(action='ignore', category=FutureWarning)


def hits():
    user_follow = pd.read_csv('data/users.csv')
    user_follow_d = user_follow.drop_duplicates()
    g = nx.DiGraph()
    for database_id, followers, following in user_follow_d.values:
        if followers:
            followers = str(followers).split(",")
            for follower in followers:
                g.add_edge(database_id, follower)
        if following:
            following = str(following).split(",")
            for one_following in following:
                g.add_edge(one_following, database_id)
    print('start')

    h, a = nx.hits(g)
    print('end')
    with open("./result/hits_h.txt", "w") as f:
        f.write("id\th\n")
        for key in h:
            f.write(str(key) + "\t" + str(h[key]) + "\n")

    with open("./result/hits_a.txt", "w") as f:
        f.write("id\ta\n")
        for key in a:
            f.write(str(key) + "\t" + str(a[key]) + "\n")
    print('save')


if __name__ == '__main__':
    hits()
