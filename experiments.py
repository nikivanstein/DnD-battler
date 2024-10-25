__author__ = 'Matteo'
__doc__ = """
The reason why I wrote the script was to run some tests.
"""

N = "\n"
T = "\t"
# N="<br/>"

import pandas as pd
import DnD_battler, csv
import seaborn as sns
import matplotlib.pyplot as plt


def cr_appraisal(party):
    """
    Assess the victory probability of each monster in the manual against Creatures in the `party` Encounter
    :param party: a list of creatures
    :return:
    """
    # set to same team
    for pc in party:
        pc.alignment = "players"
    #out = csv.DictWriter(open("CR stats.csv", 'w', newline=''),
    #                     fieldnames=['beast', 'victory'])  # DnD_battler.Encounter().json() is overkill and messy
    
    win_dict = {}
    #out.writeheader()
    # challenge each monster
    for beastname in DnD_battler.Creature.beastiary:
        beast = DnD_battler.Creature.load(beastname)
        beast.alignment = "opponent"
        party.append(beast)  # seems a bit wrong, but everything gets hard reset
        party.go_to_war(100)
        #print(beastname + ": " + str(party.tally['victories']['players']) + "%")
        win_dict[beastname] = party.tally['victories']['players']
        #out.writerow({'beast': beastname, 'victory': party.tally['victories']['players']})
        party.remove(beast)  # will perform a hard reset by default

    return win_dict



def dice_variance(d):
        return sum([sum([(i+1-(d2+1)/2)**2 for i in range(d2)])/d2 for d2 in d.num_faces])

if __name__ == "__main__":
    beast_dict = {}
    for beastname in DnD_battler.Creature.beastiary:
        print("Processing ", beastname)
        beast = DnD_battler.Creature.load(beastname)
        beast.alignment = "players"
        
        beast_dict[beastname] = cr_appraisal(DnD_battler.Encounter(beast))
        beast_dict[beastname]['CR'] = float(beast.cr)
        beast_dict[beastname]['HP'] = int(beast.hp)
    df = pd.DataFrame.from_dict(beast_dict).T
    df.to_csv('monster_victories.csv', index=False) 
    print(df)
    #commoner_brawl()
    #print(dice_variance(DnD_battler.Dice(0, num_faces=[100], role="damage")))

    # Assume each row and column in df represents a different monster
    # Calculate the average number of wins across the columns for each monster
    win_data = df.drop(columns=['CR', 'HP'])  # Keep only win data for heatmap
    win_data = win_data.apply(pd.to_numeric, errors='coerce')
    win_data = win_data.fillna(0)

    df['average_wins'] = win_data.mean(axis=1)

    win_data['average_wins'] = win_data.mean(axis=1)
    win_data = win_data.sort_values(by='average_wins', ascending=False)

    # Drop the 'average_wins' column for the heatmap (only use it for sorting)
    heatmap_data = win_data.drop(columns=['average_wins'])

    # Sort DataFrames for plots that require sorted data
    df_by_cr = df.sort_values(by='CR')
    df_by_hp = df.sort_values(by='HP')

    # 1. Heatmap of Wins Between Monsters
    plt.figure(figsize=(12, 10))
    sns.heatmap(heatmap_data, annot=False, cmap='YlGnBu', cbar=True)
    plt.title("Win Probability Heatmap Between Monsters")
    plt.xlabel("Opponent Monsters")
    plt.ylabel("Monsters")
    plt.tight_layout()
    plt.savefig("heatmap_monsters.png")
    plt.clf()

    # 2. Scatter Plot of Average Wins vs. Challenge Rating
    plt.figure(figsize=(10, 6))
    plt.scatter(df_by_cr['CR'], df_by_cr['average_wins'])
    plt.title("Average Wins vs Challenge Rating")
    plt.xlabel("Challenge Rating")
    plt.ylabel("Average Wins")
    plt.tight_layout()
    plt.savefig("average_wins_per_cr.png")
    plt.clf()

    # 3. Scatter Plot of Average Wins vs HP
    plt.figure(figsize=(10, 6))
    plt.scatter(df_by_hp['HP'], df_by_hp['average_wins'])
    plt.title("Average Wins vs HP")
    plt.xlabel("HP")
    plt.ylabel("Average Wins")
    plt.tight_layout()
    plt.savefig("average_wins_per_HP.png")
