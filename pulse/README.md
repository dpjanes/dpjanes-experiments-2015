Experiments with encoding IR pulses into something that's
relatively compact and relatively easy to decode

# Important Links:

This has the circuits and most of the useful stuff

http://alexba.in/blog/2013/01/06/setting-up-lirc-on-the-raspberrypi/

# Recording Raw Bytes

    sudo /etc/init.d/lirc stop
    mode2 -d /dev/lirc0

# Converting LIRC.conf raw files to our format (in JSON)

    python raw.py data/lirc.conf

