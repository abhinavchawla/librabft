from generator import scenario_generator
import json

if __name__=='__main__':
    with open("generator_config.json", "r") as read_file:
        data = json.load(read_file)

    scenario_generator = scenario_generator(config=data)
    scenario = scenario_generator.generate_scenario()
    while scenario:
        print(scenario)
        scenario = scenario_generator.generate_scenario()