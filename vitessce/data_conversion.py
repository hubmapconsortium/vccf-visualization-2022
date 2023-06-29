import os
import sys
import pandas as pd
import numpy as np


def generate_cell_vertices(x, y, z, radius, num_vertices=12):
    angles = np.linspace(0, 2 * np.pi, num_vertices)
    vertices = [(x + np.cos(angle) * radius, y + np.sin(angle) * radius, z) for angle in angles]
    return vertices


def generate_random_cell_vertices(x, y, z, radius, num_vertices=12):
    angles = np.linspace(0, 2 * np.pi, num_vertices)
    vertices = []
    # Add randomness to radius and angle
    random_radius = np.random.uniform(0.9 * radius, 1.1 * radius)
    for angle in angles:
        random_angle = np.random.uniform(-0.2, 0.2)  # adjust as needed
        vertices.append(
            (x + np.cos(angle + random_angle) * random_radius, y + np.sin(angle + random_angle) * random_radius, z))
    vertices.append(vertices[0])
    return vertices


def generate_link_vertices(x, y, z, vx, vy, vz):
    return [(x, y, z), (vx, vy, vz)]


def main():
    # Default region_index
    region_index = 3

    # Check if at least one command-line argument is given
    if len(sys.argv) >= 2:
        # Use the given argument as region_index
        region_index = int(sys.argv[1])

    # Construct the path to the nuclei file
    nuclei_root_path = rf'G:\GE\skin_12_data\region_{region_index}'
    nuclei_file_name = 'nuclei.csv'
    vessel_file_name = 'vessel.csv'
    nuclei_file_path = os.path.join(nuclei_root_path, nuclei_file_name)
    vessel_file_path = os.path.join(nuclei_root_path, vessel_file_name)

    # read the csv file
    df = pd.read_csv(nuclei_file_path)

    # filter out the rows where type is one of the specified values
    cell_types = ['T-Killer', 'T-Helper', 'T-Reg', 'CD68']
    average_sizes = {'T-Killer': 15.89, 'T-Helper': 16.96, 'T-Reg': 17.75, 'CD68': 16, 'CD31': 16}
    filtered_df = df[df['type'].isin(cell_types)]

    # construct the 'cell' table and generate vertices
    cell_table = filtered_df[['type', 'x', 'y', 'z']].copy()
    cell_table['vertices'] = cell_table.apply(
        lambda row: generate_random_cell_vertices(row['x'], row['y'], row['z'], average_sizes[row['type']]), axis=1)

    # construct the 'link' table and generate vertices
    link_table = filtered_df[['type', 'x', 'y', 'z', 'vx', 'vy', 'vz']].copy()
    link_table['vertices'] = link_table.apply(
        lambda row: generate_link_vertices(row['x'], row['y'], row['z'], row['vx'], row['vy'], row['vz']), axis=1)
    link_table['type'] = link_table['type'].apply(lambda x: x + '_link')

    # read the vessel csv file
    vessel_df = pd.read_csv(vessel_file_path)
    # add a new 'type' column with 'vessel' as its value
    vessel_df['type'] = 'vessel'
    # construct the 'cell' table for the vessel data and generate vertices
    # Here I used a fixed radius for 'vessel', adjust as needed
    vessel_df['vertices'] = vessel_df.apply(
        lambda row: generate_random_cell_vertices(row['x'], row['y'], row['z'], radius=average_sizes['CD31']), axis=1)

    # append the vessel data to the cell_table
    cell_table = pd.concat([cell_table, vessel_df], ignore_index=True)

    # Save the tables to .csv files
    cell_table.to_csv(os.path.join(nuclei_root_path, 'cell_table.csv'), index=False)
    link_table.to_csv(os.path.join(nuclei_root_path, 'link_table.csv'), index=False)


if __name__ == '__main__':
    main()
