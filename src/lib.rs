use std::env;
use std::path::PathBuf;
use std::process::Command;

pub fn generate_version() {
    let out_dir = PathBuf::from(env::var("OUT_DIR").unwrap());
    let generated_file = out_dir.join("version.rs");
    // The path to the folder containing the python module
    let src_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("src");

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
        // env::var syntax gets calling crate's location
        .arg(PathBuf::from(env::var("CARGO_MANIFEST_DIR").unwrap()))
        .arg("--cargo")
        .arg(PathBuf::from(env::var("CARGO_PKG_VERSION").unwrap()));

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

    // Re-run if python module is modified
    println!("cargo:rerun-if-changed={}", src_dir.display());

    // Re-build calling crate if output file changes
    println!("cargo:rerun-if-changed={}", generated_file.display());
}
