from random import randint, seed, random, sample
from time import time
# 1589148085.5775692
import operator
from functools import reduce
import matplotlib.pyplot as plt
import pandas as pd


class GeneticAlgorithm(object):

    def __init__(self):
        self.aux = AuxClass()
        self.new_generation = []

    def run_genetic_algorithm(self, goal):
        i = 1
        min_aptitudes = []
        aptitudes_avg = []
        population = self.generate_population(8)
        print("Population: ", population)

        while True:
            if goal in population:
                hamming_distance = self.aux.calculate_hamming(population, goal)
                aptitudes = self.aux.calculate_aptitude(hamming_distance, 14)
                aptitudes_avg.append(
                    (reduce(operator.add, aptitudes)/len(aptitudes)))
                min_aptitudes.append(min(aptitudes))
                break
            hamming_distance = self.aux.calculate_hamming(population, goal)
            aptitudes = self.aux.calculate_aptitude(hamming_distance, 14)
            aptitudes_avg.append(
                (reduce(operator.add, aptitudes)/len(aptitudes)))
            min_aptitudes.append(min(aptitudes))
            roulette_needles = self.aux.define_needle_points(8)
            stallions = self.select(aptitudes, population, roulette_needles)
            new_generation = self.reproduce(stallions)
            mutated_new_generation = self.mutate(new_generation)

            i += 1
            population = mutated_new_generation

        return [population, i, min_aptitudes, aptitudes_avg]

    def generate_population(self, indiv_number, _seed=time()):
        print("Seed: ", _seed)
        seed(_seed)
        population = []

        for individual in range(indiv_number):
            population.append(self.aux.to_bin(randint(0, 4095)))

        return population

    def select(self, aptitude, population, needle_points):
        individuals_score = self.aux.define_individuals_score(aptitude)
        population_scores = self.aux.group_sort_population_score(
            population, individuals_score)
        roulette = self.aux.define_roulette_positions_values(population_scores)
        selected_individuals = self.aux.select_individuals(
            roulette, needle_points)
        return selected_individuals

    def reproduce(self, stallions):
        population_pair = self.aux.pair_stallions(stallions)
        cross_chances = self.aux.generate_random_chance(population_pair)
        new_generation = self.cross_over(
            population_pair, cross_chances, randint(3, (len(population_pair[0][0])-1)))
        return new_generation

    def cross_over(self, population_pair, cross_chances, crop, Pc=0.6):
        self.new_generation = []
        i = 0
        while i < len(cross_chances):
            if cross_chances[i] <= Pc:
                individuals_pair = self.make_cross_over(
                    population_pair[i], crop)
                self.make_new_generation(individuals_pair)
            else:
                self.make_new_generation(population_pair[i])
            i += 1
        return self.new_generation

    def make_cross_over(self, population_pair, crop):
        cropped_start = []
        cropped_end = []
        for individual in population_pair:
            cropped_start.append(individual[2:crop])
            cropped_end.append(individual[crop:])
        return ["0b" + cropped_start[0] + cropped_end[1], "0b" + cropped_start[1] + cropped_end[0]]

    def make_new_generation(self, population_pair):
        for individual in population_pair:
            self.new_generation.append(individual)

    def mutate(self, population):
        mutated_list = []
        for individual in population:
            mutated_individual = ['0', 'b']
            i = 2
            while i < len(individual):
                bit = self.transform_bit(individual[i])
                mutated_individual.append(bit)
                i += 1

            mutated_list.append(''.join(mutated_individual))
        return mutated_list

    def transform_bit(self, bit):
        random_chance = random()
        if random_chance <= 0.02:
            bit = '0' if bit == '1' else '1'
        return bit


class AuxClass(object):
    def to_bin(self, int_number):
        return format(int_number, '#014b')

    def to_number(self, bin_number):
        return int(bin_number, 2)

    def calculate_hamming(self, population, goal):
        hamming_distance = []
        for individual in population:
            hamming_distance.append(self.hamming(goal, individual))
        return hamming_distance

    def hamming(self, seq_1, seq_2):
        index = 0
        min_length = min(len(seq_1), len(seq_2))
        max_length = max(len(seq_1), len(seq_2))
        for i in range(min_length):
            if seq_1[i] != seq_2[i]:
                index = index + 1
        index = index + (max_length - min_length)
        return index

    def calculate_aptitude(self, hamming_distance, indiv_length):
        # removing two because binary, in pyhton, start with 0b
        indiv_length = indiv_length - 2
        points = []
        for point in hamming_distance:
            points.append(indiv_length - point)
        return points

    def define_needle_points(self, needle_points):
        needles = []
        random_needles = []
        space = 1 / needle_points
        space_it = space
        needle = 0
        while needle <= 1:
            needles.append(round(needle, 2))
            needle = space_it
            space_it += space
        for needle in needles:
            random_needles.append(needle*360)
        return random_needles

    def define_individuals_score(self, population):
        elements_value = []
        elements_sum = reduce(operator.add, population)
        for individual in population:
            elements_value.append(individual/elements_sum)
        return elements_value

    def group_sort_population_score(self, scores, population):
        population_score = []
        i = 0
        while i < len(population):
            population_score.append([population[i], scores[i]])
            i += 1
        return sample(population_score, len(population_score))

    def define_roulette_positions_values(self, population_score):
        i = 0
        prev_value = 0
        roulette = []
        while i < len(population_score):
            degrees = prev_value + (population_score[i][0] * 360)
            roulette.append([prev_value, degrees, population_score[i][1]])
            prev_value = float(roulette[-1][1])
            i += 1
        return roulette

    def select_individuals(self, roulette, roulette_needles):
        selecteds = []
        for needles in roulette_needles:
            for individual in roulette:
                if needles > individual[0] and needles <= individual[1]:
                    selecteds.append(individual[2])
        return selecteds

    def pair_stallions(self, population):
        population_pair = []
        i = 2
        while i <= len(population):
            population_pair.append(population[(i-2):i])
            i += 2
        return population_pair

    def generate_random_chance(self, population_pair):
        chances = []
        for chance in population_pair:
            chances.append(random())
        return chances

    def plot_poits(self, min_aptitude, aptitude_avg):
        df = pd.DataFrame(
            {"aptitude": min_aptitude, "aptitude_AVG": aptitude_avg})
        plt.subplot(211)
        plt.plot("aptitude", data=df, color="red")
        plt.title("Min. aptitude and aptitude AVG")
        plt.ylabel("Min. aptitude")

        plt.subplot(212)
        plt.plot("aptitude_AVG", data=df, color="green")
        plt.xlabel("Interactions")
        plt.ylabel("Aptitude AVG")
        plt.show()


def main():
    genetic = GeneticAlgorithm()
    aux = AuxClass()

    start_time = time()
    results = genetic.run_genetic_algorithm('0b111101101111')
    print("Final Generation: ", results[0])
    print("Interactions: ", results[1])
    print("Time: ", time() - start_time)

    aux.plot_poits(results[2], results[3])


if __name__ == "__main__":
    main()
