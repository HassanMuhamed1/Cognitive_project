import tetris_game
import ast

def load_best_chromosome(filename='best_chromosome.txt'):
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('Best Chromosome:'):
                # Extract the list part and safely evaluate it
                chromo_str = line.split(':', 1)[1].strip()
                chromosome = ast.literal_eval(chromo_str)
                return chromosome
    raise ValueError("Best Chromosome not found in file.")

# Example usage:
best_chromosome = load_best_chromosome()
print("Extracted chromosome:", best_chromosome)

final_score = tetris_game.run_tetris_simulation(best_chromosome, iterations=600)

with open('final_test_score.txt', 'w') as f:
    f.write(f"Best Chromosome: {best_chromosome}\n")
    f.write(f"Final Score (600 iterations): {final_score}\n")

print("Final test complete. Results saved to final_test_score.txt")
print(f"Final Score (600 iterations): {final_score}\n")