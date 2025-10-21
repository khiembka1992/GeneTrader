import re
import glob

def extract_fitness(line):
    match = re.search(r'Final Fitness: ([-\d.]+)$', line)
    return float(match.group(1)) if match else None

def extract_generation(line):
    match = re.search(r'Generation: (\d+)', line)
    return int(match.group(1)) if match else None

def extract_strategy_name(line):
    match = re.search(r'Strategy: (\S+)', line)
    return match.group(1) if match else None

def extract_win_rate(line):
    match = re.search(r'Win Rate: ([\d.]+)', line)
    return float(match.group(1)) if match else None

def get_config_file(strategy_name):
    last_four_digits = strategy_name[-4:]
    config_files = glob.glob(f"user_data/temp_*_{last_four_digits}.json")
    return config_files[0] if config_files else None

    

generations = {}
current_gen = None

with open('logs/fitness_log.txt', 'r') as file:
    for line in file:
        gen = extract_generation(line)
        if gen is not None:
            current_gen = gen
            if current_gen not in generations:
                generations[current_gen] = {
                    'max_fitness': None,
                    'max_fitness_line': '',
                    'strategy_name': '',
                    'win_rate': None
                }
        
        fitness = extract_fitness(line)
        win_rate = extract_win_rate(line)
        if fitness is not None and current_gen is not None:
            if generations[current_gen]['max_fitness'] is None or fitness > generations[current_gen]['max_fitness']:
                generations[current_gen]['max_fitness'] = fitness
                generations[current_gen]['max_fitness_line'] = line.strip()
                generations[current_gen]['strategy_name'] = extract_strategy_name(line)
                generations[current_gen]['win_rate'] = win_rate


if generations:
    overall_max_fitness = float('-inf')
    overall_best_gen = None

    for gen, data in sorted(generations.items()):
        if data['max_fitness'] is not None:
            print(f"Generation {gen} max fitness:")
            print(data['max_fitness_line'])
            print(f"Maximum fitness: {data['max_fitness']}")
            print(f"Win Rate: {data['win_rate']}")
            
            strategy_name = data['strategy_name'][:-1]
            config_file = get_config_file(strategy_name)
            if config_file:
                backtesting_command = f"/Users/zhangjiawei/Projects/freqtrade/.venv/bin/freqtrade backtesting --strategy {strategy_name} -c {config_file} --timerange 20240101- --timeframe-detail 1m > generation_{gen}.txt"
            else:
                print(f"Warning: No matching config file found for strategy {strategy_name}")
            print()

            if data['max_fitness'] > overall_max_fitness:
                overall_max_fitness = data['max_fitness']
                overall_best_gen = gen
        else:
            print(f"Generation {gen}: No valid fitness values found\n")

    if overall_best_gen is not None:
        print("Overall best fitness:")
        print(generations[overall_best_gen]['max_fitness_line'])
        print(f"Maximum fitness: {overall_max_fitness}")

        best_strategy_name = generations[overall_best_gen]['strategy_name'][:-1]
        best_config_file = get_config_file(best_strategy_name)
        
        print(best_config_file)
        print(best_strategy_name)
        if best_config_file:                
            best_backtesting_command = f"/Users/zhangjiawei/Projects/freqtrade/.venv/bin/freqtrade backtesting --strategy {best_strategy_name} -c {best_config_file} --timerange 20240401- --timeframe-detail 1m > best_generation_{overall_best_gen}.txt"
            print("Best strategy backtesting command:")
            print(best_backtesting_command)
        else:
            print(f"Warning: No matching config file found for best strategy {best_strategy_name}")
else:
    print("No valid generations or fitness values found in the file.")

print("\nDebug information:")
print(f"Total generations processed: {len(generations)}")
print(f"Found any fitness values: {'Yes' if any(gen['max_fitness'] is not None for gen in generations.values()) else 'No'}")
