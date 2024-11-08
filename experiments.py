import pandas as pd
import DnD_battler
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import textalloc as ta
import tqdm

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
    for beastname in tqdm.tqdm(DnD_battler.Creature.beastiary, leave=False):
        beast = DnD_battler.Creature.load(beastname)
        beast.alignment = "opponent"
        party.append(beast)  # seems a bit wrong, but everything gets hard reset
        party.go_to_war(100)
        #print(beastname + ": " + str(party.tally['victories']['players']) + "%")
        win_dict[beastname] = party.tally['victories']['players']
        # if party.tally['victories']['players'] < 100 and party.tally['victories']['players'] > 0:
        #      print(party.tally['victories']['players'])
        #out.writerow({'beast': beastname, 'victory': party.tally['victories']['players']})
        party.remove(beast)  # will perform a hard reset by default

    return win_dict



def dice_variance(d):
        return sum([sum([(i+1-(d2+1)/2)**2 for i in range(d2)])/d2 for d2 in d.num_faces])

if __name__ == "__main__":
    beast_dict = {}
    for beastname in tqdm.tqdm(DnD_battler.Creature.beastiary):
        #print("Processing ", beastname)
        beast = DnD_battler.Creature.load(beastname)
        beast.alignment = "players"
        
        beast_dict[beastname] = cr_appraisal(DnD_battler.Encounter(beast))
        beast_dict[beastname]['CR'] = float(beast.cr)
        beast_dict[beastname]['HP'] = int(beast.hp)
        beast_dict[beastname]['type'] = beast.type
    df = pd.DataFrame.from_dict(beast_dict).T
    df.to_csv('monster_victories.csv', index=False) 
    print(df)
    #commoner_brawl()
    #print(dice_variance(DnD_battler.Dice(0, num_faces=[100], role="damage")))

    file_path_beastiary = 'DnD_battler/beastiary.csv'
    df_beastiary = pd.read_csv(file_path_beastiary)

    # Create a color palette based on unique monster types
    unique_types = df['type'].unique()
    colors = cm.rainbow(np.linspace(0, 1, len(unique_types)))
    color_map = dict(zip(unique_types, colors))
    df['color'] = df['type'].map(color_map)

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
    plt.figure(figsize=(40, 40))
    sns.heatmap(heatmap_data, annot=False, cmap='YlGnBu', cbar=False)
    plt.title("Win Probability Heatmap Between Monsters")
    plt.xlabel("Opponent Monsters")
    plt.ylabel("Monsters")
    plt.tight_layout()
    plt.savefig("heatmap_monsters.png")
    plt.clf()


        
    # 1. Scatter Plot of Average Wins vs. Challenge Rating with Labels and Colors
    plt.figure(figsize=(18, 10))
    x_cr = df_by_cr['CR']
    y_cr = df_by_cr['average_wins']
    colors_cr = df_by_cr['color']
    text_list_cr = df_by_cr.index
    plt.scatter(x_cr, y_cr, c=colors_cr)

    ta.allocate(plt.gca(), x_cr, y_cr, text_list_cr, draw_all=True, x_scatter=x_cr, y_scatter=y_cr, textsize=10, max_distance=0.2, linecolor='k', textcolor=colors_cr, avoid_crossing_label_lines=True, linewidth=0.5)

    plt.title("Average Wins vs Challenge Rating")
    plt.xlabel("Challenge Rating")
    plt.ylabel("Average Wins")
    plt.tight_layout()
    plt.savefig("average_wins_per_cr_annotated.png")
    plt.clf()

    # 2. Scatter Plot of Average Wins vs HP with Labels and Colors
    plt.figure(figsize=(18, 10))
    x_hp = df_by_hp['HP']
    y_hp = df_by_hp['average_wins']
    colors_hp = df_by_hp['color']
    text_list_hp = df_by_hp.index
    plt.scatter(x_hp, y_hp, c=colors_hp)

    ta.allocate(plt.gca(), x_hp, y_hp, text_list_hp, draw_all=True, x_scatter=x_cr, y_scatter=y_cr, textsize=10, max_distance=0.2, linecolor='k', textcolor=colors_hp, avoid_crossing_label_lines=True, linewidth=0.5)

    plt.title("Average Wins vs HP")
    plt.xlabel("HP")
    plt.ylabel("Average Wins")
    plt.tight_layout()
    plt.savefig("average_wins_per_HP_annotated.png")
    plt.clf()
