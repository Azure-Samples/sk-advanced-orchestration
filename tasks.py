from invoke import task


@task
def run_chat(c):
    c.run("cd src/chat && chainlit run -w chat.py")
