from reddit import initialize_db, get_all_unique_subreddits
import time
import json
from main import update_data


if __name__ == "__main__":
    colors = {
        'black': '\033[30m',
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        'bright_black': '\033[90m',
        'bright_red': '\033[91m',
        'bright_green': '\033[92m',
        'bright_yellow': '\033[93m',
        'bright_blue': '\033[94m',
        'bright_magenta': '\033[95m',
        'bright_cyan': '\033[96m',
        'bright_white': '\033[97m',
        'reset': '\033[0m',
    }

    print(colors["red"] + """
INSIGHT RED - A Reddit LLM Tool                          
""" + colors["reset"])

    subreddits = []
    while (True):
        subreddit = input("{}(Hit ENTER To Exist) {}Sub-Reddit URL:{} ".format(
            colors["yellow"], colors["green"], colors["reset"]))

        if len(subreddit) == 0:
            break

        if "www.reddit.com" not in subreddit:
            print(
                "{}inputted Sub-Reddit URL is NOT valid, try again!{}".format(colors["red"], colors["reset"]))
        else:
            subreddits.append(subreddit.replace(" ", ""))

    print("\n• • •\n")

    post_limit = None
    while (True):
        post_per_subreddit = input(
            "{}(INT Type) Number Of Posts Scanned Per Sub-Reddit: {} ".format(colors['blue'], colors["reset"]))

        if len(post_per_subreddit) == 0:
            post_limit = 0
            break

        try:
            post_limit = int(post_per_subreddit)
            break
        except:
            post_limit = None
            print(
                "{}input MOST be type int!{}".format(colors["red"], colors["reset"]))

    print("\n• • •\n")

    earlist_epoch_time_sec = None
    while (True):

        print("{}(FLOAT/INT Type) Earlist Epoch Time (Seconds):{} ".format(
            colors['cyan'], colors["reset"]))
        print("{}   1 day ago = {} epoch seconds{}".format(
            colors["cyan"], time.time() - (60 * 60 * 24), colors["reset"]))
        print("{}   3 days ago = {} epoch seconds{}".format(
            colors["cyan"], time.time() - (60 * 60 * 24 * 3), colors["reset"]))
        print("{}   1 week ago = {} epoch seconds{}".format(
            colors["cyan"], time.time() - (60 * 60 * 24 * 7), colors["reset"]))
        print("{}   2 weeks ago = {} epoch seconds{}".format(
            colors["cyan"], time.time() - (60 * 60 * 24 * 14), colors["reset"]))
        print("{}   1 month ago = {} epoch seconds{}".format(
            colors["cyan"], time.time() - (60 * 60 * 24 * 31), colors["reset"]))
        input_epoch = input(
            "{}EPOCH VALUE:{} ".format(colors["cyan"], colors["reset"]))

        if len(input_epoch) == 0:
            earlist_epoch_time_sec = 0
            break

        try:
            earlist_epoch_time_sec = float(input_epoch.replace(" ", ""))
            if earlist_epoch_time_sec >= 0:
                break
            else:
                print(
                    "{}input MOST be greater then or equal to zero!{}".format(colors["red"], colors["reset"]))
        except:
            earlist_epoch_time_sec = None
            print(
                "{}input MOST be type float/int!{}".format(colors["red"], colors["reset"]))

    print("\n• • •\n")

    session = initialize_db(log_it=False)
    uniq_subreddits = get_all_unique_subreddits(session)

    subreddits_to_ignore = []
    if len(uniq_subreddits) > 0:
        print("Sub-Reddits In local Database:")
        for i in range(len(uniq_subreddits)):
            print("   {}) {}".format(i, uniq_subreddits[i]))
        print("\nWhich Sub-Reddit(s) would you like to ignore?\n")
        while (True):
            selected_usr = input(
                "(INT) (Hit ENTER To Exist) Sub-Reddit (ID) To Ignore: ")

            if len(selected_usr) == 0:
                break

            try:
                selected_usr = int(selected_usr)
                if selected_usr < 0 or selected_usr > len(uniq_subreddits)-1:
                    print("{}input MOST be between {} & {}! {}".format(
                        colors["red"], 0, len(uniq_subreddits)-1, colors["reset"]))
                else:
                    subreddits_to_ignore.append(uniq_subreddits[selected_usr])
            except:
                post_limit = None
                print(
                    "{}input MOST be type int!{}".format(colors["red"], colors["reset"]))

    print("\n• • •\n")

    product_description = input("{}PRODUCT DESCRIPTION:{} ".format(
        colors['magenta'], colors["reset"]))

    print("\n• • •\n")

    print("\n\n\n{}Processing...{}\n".format(colors["red"], colors["reset"]))

    output = update_data(product_description, subreddits_to_ignore,
                         earlist_epoch_time_sec, subreddits, post_limit)

    print("\n• • •\n")

    print("{}FINAL RESULTS:{}\n".format(colors["green"], colors["reset"]))

    print(json.dumps(output, indent=4))
