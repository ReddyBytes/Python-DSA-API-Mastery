import os

BASE_DIR = "python-complete-mastery"

structure = {
    "01_python_fundamentals": ["theory.md", "practice.py", "edge_cases.py", "interview.md"],
    "02_control_flow": ["theory.md", "practice.py", "pattern_programs.py", "interview.md"],
    "03_functions": ["theory.md", "practice.py", "advanced_patterns.py", "functional_programming.py", "interview.md"],
    "04_data_structures": ["theory.md", "list_practice.py", "dict_practice.py", "set_practice.py", "tuple_practice.py", "complexity_analysis.md", "interview.md"],
    "05_oops": ["theory.md", "practice.py", "advanced_practice.py", "design_patterns.py", "real_world_examples.py", "interview.md"],
    "06_exceptions_error_handling": ["theory.md", "custom_exceptions.py", "error_handling_patterns.py", "interview.md"],
    "07_modules_packages": ["theory.md", "imports_examples.py", "interview.md"],
    "08_file_handling": ["theory.md", "file_operations.py", "json_yaml_csv_handling.py", "interview.md"],
    "09_logging_debugging": ["theory.md", "logging_examples.py", "structured_logging.py", "interview.md"],
    "10_decorators": ["theory.md", "function_decorators.py", "class_decorators.py", "interview.md"],
    "11_generators_iterators": ["theory.md", "generators.py", "iterators.py", "memory_comparison.py", "interview.md"],
    "12_context_managers": ["theory.md", "custom_context_manager.py", "interview.md"],
    "13_concurrency": ["theory.md", "multithreading.py", "multiprocessing.py", "async_programming.py", "asyncio_examples.py", "interview.md"],
    "14_memory_management": ["theory.md", "gc_examples.py", "memory_optimization.py", "interview.md"],
    "15_advanced_python": ["dunder_methods.py", "operator_overloading.py", "dataclasses_examples.py", "slots_example.py", "descriptors.py", "metaclasses.py", "introspection.py", "callable_objects.py", "interview.md"],
    "16_design_patterns": ["singleton.py", "factory.py", "strategy.py", "observer.py", "dependency_injection.md", "interview.md"],
    "17_testing": ["theory.md", "unittest_examples.py", "pytest_examples.py", "mocking_examples.py", "interview.md"],
    "18_performance_optimization": ["profiling.md", "timeit_examples.py", "cProfile_examples.py", "optimization_patterns.py", "interview.md"],
    "19_production_best_practices": ["project_structure.md", "packaging.md", "environment_management.md", "coding_standards.md", "interview.md"],
    "20_system_design_with_python": ["scalable_app_design.md", "api_design_principles.md", "rate_limiter.py", "caching_examples.py", "interview.md"],
    "21_data_engineering_applications": ["file_processing_pipeline.py", "api_data_collector.py", "streaming_simulation.py", "memory_efficient_etl.py", "interview.md"],
    "99_interview_master": ["python_0_2_years.md", "python_3_5_years.md", "scenario_based_questions.md", "tricky_edge_cases.md"],
}

def create_structure():
    os.makedirs(BASE_DIR, exist_ok=True)

    # Create README
    readme_path = os.path.join(BASE_DIR, "README.md")
    with open(readme_path, "w") as f:
        f.write("# Python Complete Mastery\n\nStructured learning from basics to advanced.\n")

    for folder, files in structure.items():
        folder_path = os.path.join(BASE_DIR, folder)
        os.makedirs(folder_path, exist_ok=True)

        for file in files:
            file_path = os.path.join(folder_path, file)
            with open(file_path, "w") as f:
                f.write(f"# {file.replace('_', ' ').replace('.py', '').replace('.md', '').title()}\n\n")

    print("Repository structure created successfully!")

if __name__ == "__main__":
    create_structure()
