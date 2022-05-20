import os
import pandas as pd
import numpy as np


class BurstBiRank:
    def __init__(self, actor_limit, repo_limit):
        self.data = self.get_data()
        self.data_c = self.preprocessing(actor_limit, repo_limit)
        self.w, self.W, self.actor_id_list, self.repo_id_list = self.weight_init()
        self.S, self.u_0, self.p_0 = self.weight_normalize()
        self.u = np.ones(len(self.actor_id_list)) / len(self.actor_id_list)
        self.p = np.ones(len(self.repo_id_list)) / len(self.repo_id_list)
        self.gamma_ = 0.85
        self.lambda_ = 0.85

    def rank(self, delta=1e-6):
        for i in range(100):
            temp_u = self.u
            temp_p = self.p
            self.u = self.gamma_ * np.dot(self.S, self.p) + (1 - self.gamma_) * self.u_0
            self.p = self.lambda_ * np.dot(self.S.T, self.u) + (1 - self.lambda_) * self.p_0
            delta_u = np.mean(abs(temp_u - self.u))
            delta_p = np.mean(abs(temp_p - self.p))
            print("step", i, "delta", delta_p, delta_u)
            if delta_u < delta and delta_p < delta:
                break
        return self.u, self.p

    @staticmethod
    def get_data():
        datafiles = os.listdir('./data/log')
        datalist = []
        for datafile in datafiles:
            if datafile[0:3] == 'log':
                datalist.append(pd.read_csv('./data/log/' + datafile, index_col=False))
        data = pd.concat(datalist)
        return data

    def preprocessing(self, actor_limit, repo_limit):
        data = self.data

        actor_id_count = data['actor_id'].value_counts()
        actor_id_count = actor_id_count[actor_id_count > actor_limit]
        actor_id = actor_id_count.index

        repo_id_count = data['repo_id'].value_counts()
        repo_id_count = repo_id_count[repo_id_count > repo_limit]
        repo_id = repo_id_count.index

        data_c = data[data['actor_id'].isin(actor_id)]
        data_c = data_c[data_c['repo_id'].isin(repo_id)]

        data_c['created_at'] = pd.to_datetime(data_c['created_at'])
        data_c['created_at'] = pd.to_numeric(data_c['created_at'])

        return data_c

    def weight_init(self):
        w = {}
        for i in self.data_c.groupby(['actor_id', 'repo_id'])['created_at']:
            link = i[0]
            time = [int(x) for x in list(i[1])]
            time.sort()
            if len(time) == 1:
                b = 1
            else:
                time_interval = []
                prev = time[0]
                for curr in time:
                    time_interval.append(curr - prev)
                    prev = curr
                time_interval.remove(0)
                mean = np.mean(time_interval)
                std = np.std(time_interval)
                if std + mean == 0:
                    b = 1
                else:
                    b = (std - mean) / (std + mean)
            w[link] = - b + 1

        actor_id_set = set()
        repo_id_set = set()
        for i in w.keys():
            actor_id_set.add(i[0])
            repo_id_set.add(i[1])
        actor_id_list = list(actor_id_set)
        repo_id_list = list(repo_id_set)

        actor_id_list.sort()
        repo_id_list.sort()

        W = np.zeros((len(actor_id_list), len(repo_id_list)))

        for item in w.keys():
            i = actor_id_list.index(item[0])
            j = repo_id_list.index(item[1])
            W[i][j] = w[item]
        return w, W, actor_id_list, repo_id_list

    def weight_normalize(self):
        D_u = np.zeros(len(self.actor_id_list))
        D_p = np.zeros(len(self.repo_id_list))
        for item in self.w.keys():
            D_u[self.actor_id_list.index(item[0])] += 1
            D_p[self.repo_id_list.index(item[1])] += 1
        u_0 = D_u / np.sum(D_u)
        p_0 = D_p / np.sum(D_p)
        D_u = np.diag(D_u ** (-0.5))
        D_p = np.diag(D_p ** (-0.5))
        S = np.dot(np.dot(D_u, self.W), D_p)
        return S, u_0, p_0


if __name__ == '__main__':
    rank = BurstBiRank(1000, 5000)
    print("actor count", len(rank.actor_id_list))
    print("repo count", len(rank.repo_id_list))
    u, p = rank.rank()
    u = u.tolist()
    p = p.tolist()
    with open('./result/burstbirank_u.txt', 'w') as f:
        f.write("u\trank\n")
        for i in range(len(u)):
            f.write(str(rank.actor_id_list[i]) + '\t' + str(u[i]) + '\n')
    with open('./result/burstbirank_p.txt', 'w') as f:
        f.write("p\trank\n")
        for i in range(len(p)):
            f.write(str(rank.repo_id_list[i]) + '\t' + str(p[i]) + '\n')
