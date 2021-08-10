from bot.logger import log


if __name__ == '__main__':
    log.info("Starting the stickdistort")

    log.info("Initializing miscellaneous")
    from bot import misc

    log.info("Initializing bot modules")
    import bot.bot
    bot.bot.init_modules()

    log.info("Starting db updates")
    misc.db.run_updates(timeout=5)  # seconds

    log.info("Starting bot pooling")
    bot.bot.start_pooling()
