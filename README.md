# Secure HRI Workspace (ROS 2 Jazzy + SROS2)

This project demonstrates secure Node-to-Node communication in a Human-Robot Interaction (HRI) system using ROS 2 Jazzy and SROS 2. It consists of multiple nodes (`emotion_node`, `gesture_node`, `context_node`, `motion_node`, `fusion_engine_node`, and a `rogue_node` for attack simulation) communicating over a secure DDS network.

---

## 1. Environment Setup

*Work through these steps in order. Every command goes into your WSL Ubuntu 24.04 terminal unless stated otherwise. Open it now from Windows by searching "Ubuntu" in the Start menu.*

### Step 1.1 — Confirm you are on WSL2 (not WSL1)
SROS2 requires WSL2. Run this in Windows PowerShell (not WSL):
```powershell
wsl --list --verbose
```
**Expected output:**
```text
  NAME      STATE           VERSION
* Ubuntu    Running         2
```
The VERSION column must say `2`. If it says `1`, run:
```powershell
wsl --set-version Ubuntu 2
```
Then wait for it to finish before continuing.

### Step 1.2 — Check your Ubuntu version
Back in your WSL terminal:
```bash
lsb_release -a
```
**Expected output:**
```text
Description:    Ubuntu 24.04.x LTS
Codename:       noble
```

### Step 1.3 — Update the system
```bash
sudo apt update && sudo apt upgrade -y
```

### Step 1.4 — Set locale (required by ROS 2)
```bash
sudo apt install locales -y
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8
```
Verify:
```bash
locale
```
You should see `LANG=en_US.UTF-8` in the output. 

### Step 1.5 — Add the ROS 2 package repository
Run these four commands one at a time:
```bash
sudo apt install software-properties-common curl -y
sudo add-apt-repository universe
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
  -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) \
  signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
  http://packages.ros.org/ros2/ubuntu \
  $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | \
  sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
```

### Step 1.6 — Install ROS 2 Jazzy
```bash
sudo apt update
sudo apt install ros-jazzy-desktop ros-dev-tools -y
```

### Step 1.7 — Install SROS2 security dependencies
```bash
sudo apt install ros-jazzy-rmw-fastrtps-cpp \
  python3-cryptography \
  openssl -y
```

### Step 1.8 — Configure your shell environment
We add three lines to your `.bashrc` so every new terminal is ROS2-ready automatically:
```bash
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
echo "export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST" >> ~/.bashrc
echo "export RMW_IMPLEMENTATION=rmw_fastrtps_cpp" >> ~/.bashrc
```
Now reload your shell:
```bash
source ~/.bashrc
```

### Step 1.9 — Verify the ROS 2 installation
Run:
```bash
ros2 --version
```
**Sanity check:** Open two separate WSL terminal windows.
Terminal 1:
```bash
ros2 run demo_nodes_py talker
```
Terminal 2:
```bash
ros2 run demo_nodes_py listener
```
If Terminal 2 receives messages, ROS 2 is working correctly. Stop both with `Ctrl+C`.

### Step 1.10 — Verify SROS2 tools are available
```bash
ros2 security --help
```
If you see commands like `create_enclave`, `create_key`, etc., SROS 2 is ready.

### Step 1.11 — Configure VS Code
In VS Code on Windows, install:
1. **Remote - WSL** (by Microsoft)
2. **Python** (by Microsoft)

To open the project from WSL:
```bash
# Navigate to your workspace (update this to your cloned repository path)
cd /path/to/secure_hri_ws 
code .
```
You should see `WSL: Ubuntu-24.04` in the bottom-left corner in green.

---

### Phase 1 Checkpoint
Run this down to ensure everything is perfect:
```bash
echo "ROS: $(ros2 --version 2>&1 | head -1)" && \
echo "OpenSSL: $(openssl version)" && \
echo "Python: $(python3 --version)" && \
echo "FastDDS: $(ros2 pkg list | grep fastrtps)" && \
echo "SROS2: $(ros2 security --help 2>&1 | head -1)"
```

---

## 2. Building the Project

Before running the project, you must build the workspace packages.

1. Open a new terminal at the root of the workspace (`secure_hri_ws`).
2. Build using colcon:
   ```bash
   colcon build --symlink-install
   ```
3. Source the local installation:
   ```bash
   source install/setup.bash
   ```
*(Note: You must run `source install/setup.bash` in every new terminal window you open for this workspace).*

---

## 3. Running the Project

This project contains two setup scenarios: A Baseline Demo (without security) and a Secure Demo (with SROS2 enforcement).

### Scenario A: Baseline Demo (Insecure)
Run the standard HRI system without ROS2 security features enabled. This allows any node (including rogue nodes) to publish and subscribe freely.

```bash
# Make sure your workspace is sourced
source install/setup.bash

# Launch the baseline system
ros2 launch hri_secure_nodes baseline_demo.launch.py
```

### Scenario B: Secure Demo (SROS 2 Enforced)
Run the application with security strictly enforced. Nodes lacking proper certificates or attempting to publish/subscribe to unpermitted topics will be blocked.

```bash
# Make sure your workspace is sourced
source install/setup.bash

# Enable SROS 2 environment variables
export ROS_SECURITY_ENABLE=true
export ROS_SECURITY_STRATEGY=Enforce

# Point to the keystore containing the generated enclaves
# Note: Ensure this path correctly points to the 'keystore' directory in the workspace.
export ROS_SECURITY_KEYSTORE=$(pwd)/keystore

# Launch the secure system
ros2 launch hri_secure_nodes secure_demo.launch.py
```

*If you need to regenerate keys/policies in the future, use the `ros2 security generate_artifacts` tools targeting the `policies/policy.xml` file.*
