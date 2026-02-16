import os

BASE_DIR = "dsa-complete-mastery"

structure = {
    "01_complexity_analysis": ["theory.md", "examples.py", "interview.md"],
    "02_arrays": ["theory.md", "implementation.py", "practice_problems.py", "advanced_problems.py", "interview.md"],
    "03_strings": ["theory.md", "implementation.py", "practice_problems.py", "advanced_problems.py", "interview.md"],
    "04_recursion": ["theory.md", "implementation.py", "practice_problems.py", "advanced_problems.py", "interview.md"],
    "05_sorting": ["theory.md", "basic_sorting.py", "advanced_sorting.py", "practice_problems.py", "interview.md"],
    "06_searching": ["theory.md", "linear_binary_search.py", "practice_problems.py", "interview.md"],
    "07_linked_list": ["theory.md", "implementation.py", "practice_problems.py", "advanced_problems.py", "interview.md"],
    "08_stack": ["theory.md", "implementation.py", "monotonic_stack.py", "practice_problems.py", "interview.md"],
    "09_queue": ["theory.md", "implementation.py", "deque_priority_queue.py", "practice_problems.py", "interview.md"],
    "10_hashing": ["theory.md", "hashmap_set.py", "collision_handling.md", "practice_problems.py", "interview.md"],
    "11_two_pointers": ["theory.md", "implementation.py", "practice_problems.py", "interview.md"],
    "12_sliding_window": ["theory.md", "implementation.py", "practice_problems.py", "interview.md"],
    "13_binary_search": ["theory.md", "implementation.py", "search_on_answer.py", "practice_problems.py", "interview.md"],
    "14_trees": ["theory.md", "tree_traversals.py", "practice_problems.py", "advanced_problems.py", "interview.md"],
    "15_binary_search_trees": ["theory.md", "bst_operations.py", "practice_problems.py", "interview.md"],
    "16_heaps": ["theory.md", "min_max_heap.py", "heap_problems.py", "interview.md"],
    "17_trie": ["theory.md", "implementation.py", "practice_problems.py", "interview.md"],
    "18_graphs": ["theory.md", "bfs_dfs.py", "shortest_path.py", "practice_problems.py", "advanced_graph_problems.py", "interview.md"],
    "19_greedy": ["theory.md", "implementation.py", "practice_problems.py", "interview.md"],
    "20_backtracking": ["theory.md", "implementation.py", "n_queens.py", "practice_problems.py", "interview.md"],
    "21_dynamic_programming": ["theory.md", "1d_dp.py", "2d_dp.py", "knapsack.py", "practice_problems.py", "advanced_dp.py", "interview.md"],
    "22_bit_manipulation": ["theory.md", "bit_operations.py", "practice_problems.py", "interview.md"],
    "23_segment_tree": ["theory.md", "implementation.py", "lazy_propagation.py", "interview.md"],
    "24_disjoint_set_union": ["theory.md", "union_find.py", "path_compression.py", "interview.md"],
    "25_advanced_graphs": ["topological_sort.py", "strongly_connected_components.py", "minimum_spanning_tree.py", "network_flow.py", "interview.md"],
    "26_system_design_patterns": ["lru_cache.py", "rate_limiter.py", "caching_strategies.md", "interview.md"],
    "99_interview_master": ["0_2_years.md", "3_5_years.md", "faang_level_questions.md"]
}

def create_structure():
    os.makedirs(BASE_DIR, exist_ok=True)

    # Create README
    readme_path = os.path.join(BASE_DIR, "README.md")
    with open(readme_path, "w") as f:
        f.write("# DSA Complete Mastery\n\nStructured Data Structures and Algorithms learning repository.\n")

    for folder, files in structure.items():
        folder_path = os.path.join(BASE_DIR, folder)
        os.makedirs(folder_path, exist_ok=True)

        for file in files:
            file_path = os.path.join(folder_path, file)
            with open(file_path, "w") as f:
                f.write(f"# {file.replace('_', ' ').replace('.py', '').replace('.md', '').title()}\n\n")

    print("DSA repository structure created successfully!")

if __name__ == "__main__":
    create_structure()
