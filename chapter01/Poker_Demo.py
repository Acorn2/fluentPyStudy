#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
author:Herish
datetime:2019/4/24 19:55
software: PyCharm
description: 
'''
import collections

try:
    from collections.abc import MutableSequence
except ImportError:
    from collections import MutableSequence
from random import choice, shuffle
from itertools import groupby

Card = collections.namedtuple('Card', ['rank', 'suit'])

class Poker(MutableSequence):
    # 扑克牌的相关定义
    ranks = [str(n) for n in range(2, 11)] + list('JQKA')
    suits = 'spades hearts diamonds clubs'.split()  # 黑桃，红桃，方块，梅花
    suit_values = dict(spades=3, hearts=2, diamonds=1, clubs=0)#黑桃最大，红桃次之，方块再次之，梅花最小

    def __init__(self):
        self._cards = [Card(rank, suit) for rank in self.ranks
                       for suit in self.suits]

    def __len__(self):
        return len(self._cards)

    def __getitem__(self, position):  # 仅仅实现了__getitem__方法，该对象就变成可迭代的
        return self._cards[position]

    def __setitem__(self, position, value):
        self._cards[position] = value

    def __delitem__(self, position):
        del self._cards[position]

    def insert(self, position, value):
        self._cards[position] = value


Own_Poker = collections.namedtuple('Own_Poker', ['id', 'rank', 'suit', 'score'])

class Player():
    '''
    牌型　　豹子：三张同样大小的牌。　　顺金：花色相同的三张连牌。　　金花：三张花色相同的牌。　
    顺子：三张花色不全相同的连牌。　　对子：三张牌中有两张同样大小的牌。　　单张：除以上牌型的牌。
    '''

    def __init__(self, id, poker):
        self.id = id
        self.poker = poker   #一副扑克牌
        self.pokers = []#玩家手中的牌
        self.type = 0  # 每个人初始都假定为三张毫无关系的牌，也就是扑克牌赢法中的“单张”

    def set_card_score(self, card):
        '''
        按照点数判定扑克牌的大小
        :param card:扑克牌卡片
        :return:扑克牌点数大小
        '''
        rank_value = Poker.ranks.index(card.rank)
        suit_values = Poker.suit_values
        return rank_value * len(suit_values) + suit_values[card.suit]

    def sort_card_index(self, rank_index_list):
        '''
        通过值减下标的方式分组,如果三个值连续则被分配到同一个g中
        比如说ll=[3,4,5,7,8]，分组时，enumerate(ll)=[(0,3),(1,4),(2,5),(3,7),(4,8)],fun函数值减下标，结果一样的，就归为一组
        在本程序中，如果是三张连续的扑克牌，则应该是同一个g中，此时返回为Ture，否则为False
        :param rank_index_list:
        :return:
        '''
        fun = lambda x: x[1] - x[0]
        for k, g in groupby(enumerate(rank_index_list), fun):  # 返回一个产生按照fun进行分组后的值集合的迭代器.
            if len([v for i, v in g]) == 3:
                return True
        return False

    def judge_type(self):
        '''
        玩家随机发完三张牌后，根据扑克牌玩法进行区分，对手中的牌进行判别属于哪种类型
        :return:
        '''
        suit_list = []
        rank_list = []
        score_list = []
        for poker in self.pokers:
            suit_list.append(poker.suit)
            rank_list.append(poker.rank)
            score_list.append(poker.score)

        rank_index_list = []  # 扑克牌卡片在Poker中rank中的index
        for rank in rank_list:
            index = self.poker.ranks.index(rank)
            rank_index_list.append(index)

        if len(set(rank_list)) == 1:
            self.type = 5  # 豹子
        elif len(set(suit_list)) == 1:
            if self.sort_card_index(rank_index_list):
                self.type = 4  # 顺金
            else:
                self.type = 3  # 金花
        elif self.sort_card_index(rank_index_list):
            self.type = 2  # 顺子
        elif len(set(rank_list)) == 2:
            self.type = 1  # 对子

    def play(self):
        self.judge_type()


class Winner():
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2

    def get_max_card(self, player):
        '''
        筛选出三张牌中最大的牌，这里返回的是在ranks中的index
        :param player:
        :return:
        '''
        ranks = Poker.ranks
        rank_index_list = []  # 扑克牌卡片在Poker中rank中的index
        for poker in player.pokers:
            index = ranks.index(poker.rank)
            rank_index_list.append(index)
        return max(rank_index_list)

    def get_card_suit(self, player):
        '''
        返回扑克牌花色大小
        :param player:
        :return:
        '''
        suit_values = Poker.suit_values
        suit = player.pokers[0].suit
        return suit_values[suit]

    def get_card_value(self, player):
        '''
        当牌型是对子的时候，经过匹配找出是对子的牌和单个的牌，这里返回的是牌的index，便于比较大小
        :param player:
        :return:
        '''
        ranks = Poker.ranks
        rank_index_dict = {}  # 扑克牌卡片在Poker中rank中的index
        repeat_rank_value = 0  # 成对的两张扑克牌的大小
        single_rank_value = 0  # 单个的扑克牌的大小
        for poker in player.pokers:
            index = ranks.index(poker.rank)
            if index in rank_index_dict:
                rank_index_dict[index] += 1
            else:
                rank_index_dict[index] = 1
        rank_index_dict = sorted(rank_index_dict.items(), key=lambda d: d[1], reverse=True)
        n = 0
        for key in rank_index_dict:
            if n == 0:
                repeat_rank_value = key
            else:
                single_rank_value = key
            n += 1
        return repeat_rank_value, single_rank_value

    def get_player_score(self, player):
        '''
        当牌型为单牌时，计算手中的牌相加后的值大小
        :param player:
        :return:
        '''
        ranks = Poker.ranks
        score = 0
        for poker in player.pokers:
            index = ranks.index(poker.rank)  # 扑克牌卡片在Poker中rank中的index
            score += index
        return score

    def get_winner(self):
        player1, player2 = self.player1, self.player2
        # 先比较玩家手中的牌型，大的胜出,玩牌的规则暂时不涉及到牌色，如有修改可以在此基础上调整
        # 豹子> 顺金 > 金花 > 顺子 > 对子 > 单张
        if player1.type > player2.type:
            return player1
        elif player1.type < player2.type:
            return player2
        else:  # 当玩家双方手中的牌型一致时，根据赢法一一判断
            if player1.type == 5 or player1.type == 4 or player1.type == 2:  # 豹子、顺金、顺子 规则说明：按照比点
                if self.get_max_card(player1) > self.get_max_card(player2):
                    return player1
                else:
                    return player2
            elif player1.type == 1:  # 对子 规则说明：先比较相同两张的值的大小，谁大谁胜出；如果对子相同，再比较单个
                repeat_rank_value1, single_rank_value1 = self.get_card_value(player1)
                repeat_rank_value2, single_rank_value2 = self.get_card_value(player1)
                if repeat_rank_value1 > repeat_rank_value2:
                    return player1
                elif repeat_rank_value1 < repeat_rank_value2:
                    return player2
                else:
                    if single_rank_value1 > single_rank_value2:
                        return player1
                    elif single_rank_value1 < single_rank_value2:
                        return player2
                    else:
                        return None  # 平局，大家手上的牌一样大
            else:  # 单牌，金花   规则：比较所有牌的点数大小，不区分牌色
                if self.get_player_score(player1) > self.get_player_score(player2):
                    return player1
                elif self.get_player_score(player1) < self.get_player_score(player2):
                    return player2
                else:
                    return None


def compare_card(card1, card2):
    '''
    比较两种扑克牌是否相同
    :param card1:
    :param card2:
    :return: 相同返回为True，否则为False
    '''
    if card1.rank == card2.rank and card1.suit == card2.suit:
        return True
    return False


def dutch_official_work(poker, player1, player2):
    '''
    发牌人（荷官）给两位玩家轮替发牌，发出去的牌都需要从这副扑克牌中剔除出去
    :param poker: 那一副扑克牌
    :param player1:玩家1
    :param player2:玩家2
    :return:整理后的扑克牌
    '''
    def distribute_card(player):
        card = choice(poker)  # 发牌
        player.pokers.append(Own_Poker(player.id, card.rank, card.suit, player.set_card_score(card)))
        for i in range(len(poker)):
            if compare_card(card, poker[i]):
                poker.__delitem__(i)
                break

    shuffle(poker)  # 洗牌
    for k in range(3):
        distribute_card(player1)
        distribute_card(player2)

    return poker


if __name__ == '__main__':
    poker = Poker()

    # print('{0}的牌点大小为：{1}'.format(poker[8], spades_high(poker[8])))

    # 给玩家1发牌
    player1 = Player('001', poker)
    player2 = Player('002', poker)

    # 荷官发牌，模拟实际需要剔除已经发过的牌
    dutch_official_work(poker, player1, player2)

    player1.play()
    print(player1.pokers, player1.type)

    player2.play()
    print(player2.pokers, player2.type)

    # print(len(poker))
    # for i in range(len(poker)):
    #     print(poker[i], end=',')
    # print()

    # 玩家1与玩家2进行比牌，决出胜负

    ffwinner = Winner(player1, player2)
    winner = ffwinner.get_winner()
    if winner:
        print('胜者为：{0}'.format(winner.id))
    else:
        print('平局！')
