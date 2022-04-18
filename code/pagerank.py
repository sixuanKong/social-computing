import pandas as pd
import networkx as nx


def pagerank():
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

    pr = nx.pagerank(g)
    print('end')
    with open("./result/pagerank.txt", "w") as f:
        f.write("id\tpagerank\n")
        for key in pr:
            f.write(str(key) + "\t" + str(pr[key]) + "\n")
    print('save')


if __name__ == '__main__':
    pagerank()
