import subprocess
import os
import yaml

script_dir = os.path.dirname(os.path.abspath(__file__))

def load_token(filename, var):	
	with open(os.path.join(script_dir, filename), "r") as file:
		os.environ[var] = file.read().rstrip()

load_token("token_mirror.txt", "access_token")
load_token("token_merge.txt", "token")  # For archtec's merge.sh

services = {
	"minetest-mirrors": ["codeberg-org", "git-bananach-space", "notabug-org"],
	"archtec-infra": ["mirror", "merge-forks"]
}

def run():
	for repo, service_list in services.items():
		path = os.path.join(script_dir, repo)
		subprocess.run(f"git -C {path} pull", shell=True, check=True) # Update mirrorlist

		for service in service_list:
			print(f"# Service: {service}")
			with open(os.path.join(script_dir, f"{repo}/.github/workflows/{service}.yml"), "r") as file:
				mods = yaml.safe_load(file)

			for mod in mods["jobs"]["build"]["steps"]:
				if "name" in mod:
					print(f"## Working on '{mod["name"]}'")

					if service != "merge-forks":
						os.environ["branch"] = mod["env"]["branch"]
						os.environ["github_repo"] = mod["env"]["github_repo"]
						os.environ["source_repo"] = mod["env"]["source_repo"]
						subprocess.run(os.path.join(script_dir, f"{repo}/mirror.sh"), shell=True, check=True)
					else:
						os.environ["branch"] = mod["env"]["branch"]
						os.environ["repo"] = mod["env"]["repo"]
						subprocess.run(os.path.join(script_dir, f"archtec-infra/merge.sh"), shell=True, check=True)	

if __name__ == "__main__":
	try:
		run()
	except subprocess.CalledProcessError as e:
		print(f"Error in subprocess: {e}")
	except Exception as e:
		print(f"An unexpected error occurred: {e}")
