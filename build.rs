use std::env;
use std::path::PathBuf;
use std::process::Command;

fn find_git_root(start_dir: PathBuf) -> Option<PathBuf> {
    let mut current = start_dir;
    loop {
        if current.join(".git").exists() {
            return Some(current);
        }
        if !current.pop() {
            return None;
        }
    }
}

fn main() {
    let out_dir = PathBuf::from(env::var("OUT_DIR").unwrap());
    let generated_file = out_dir.join("version.rs");
    let manifest_dir = PathBuf::from(env::var("CARGO_MANIFEST_DIR").unwrap());
    // The path to the folder containing the python module
    let src_dir = manifest_dir.join("src");
    let repo_root =
        find_git_root(manifest_dir).expect("Could not find .git directory in any parent folders.");

    // Find the system Python
    // We try 'python3' first (standard for Unix), then 'python' (common for Windows)
    let python_exec = if Command::new("python3").arg("--version").status().is_ok() {
        "python3"
    } else if Command::new("python").arg("--version").status().is_ok() {
        "python"
    } else {
        panic!("Python was not found on the system path. Please install Python 3.");
    };

    // Detect enabled features
    let print_output = env::var("CARGO_FEATURE_PRINT_OUTPUT").is_ok();
    let include_time = env::var("CARGO_FEATURE_INCLUDE_TIME").is_ok();

    // Configure command
    let mut binding = Command::new(python_exec);
    let cmd = binding
        .env("PYTHONPATH", &src_dir)
        .arg("-m")
        .arg("version_builder")
        .arg("--lang")
        .arg("rust")
        .arg("--source")
        .arg("git")
        .arg("--input")
        .arg(repo_root);

    if print_output {
        cmd.arg("--print");
    }

    if include_time {
        cmd.arg("--time");
    }

    // output file is last arg
    cmd.arg(&generated_file);

    // Execute the script
    let status = cmd.status().expect("Failed to execute python script");

    if !status.success() {
        panic!("Python script failed with a non-zero exit code.");
    }

    // Re-run if the environment changes
    println!("cargo:rerun-if-env-changed=CARGO_FEATURE_PRINT_OUTPUT");
    println!("cargo:rerun-if-env-changed=CARGO_FEATURE_INCLUDE_TIME");
}
