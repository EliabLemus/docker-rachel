You must increase the size of these two constants in your php.ini file:

    upload_max_filesize = 512M
    post_max_size = 512M

This would limit uploads to 512 MB, which should be large enough for things
that can be reasonably shared from a RACHEL server. We actually have PDFs
in the CK12 module that are close to 500MB, so assuming users share
stuff like that, we shouldn't go much smaller, either.

If you are installing this on a verson of RACHEL after 20160406, it will
already be set for you.
