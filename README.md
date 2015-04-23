pyFileFixity
=========

This project aims to provide a set of open source, cross-platform, easy to use and easy to maintain (readable code) to manage data for long term storage. The project is done in pure-Python to meet those criteria.

The problem of long term storage
-----------------------------------------------
Long term storage is a very difficult topic: it's like fighting with death (in this case, the death of data). Indeed, because of entropy, data will eventually fade away because of various silent errors such as bit rot. pyFileFixity aims to provide tools to detect any data corruption, but also fight data corruption by providing repairing tools (mainly via error correction codes, which is a way to produce redundant codes from your data so that you can later repair your data using these additional pieces of information).

The best tool ever invented to recover from data corruption are the error correction codes (forward error correction), which produce n blocks for a file cut in k blocks (with k < n), and then they can rebuild the whole file with any k blocks among the total n blocks available. This can be seen as a way to average the corruption error: on average, a bit will still have the same chance to be corrupted, but since you have more bits to represent the same data, you lower the overall chance to lose this bit.

The problem is that most theoretical and pratical works on error correcting codes has been done exclusively on channel transmission (such as 4G, internet, etc.), but not on data storage, which is very different for one reason: whereas in a channel we are in a spatial scheme (both the sender and the receiver are different entities in space but working at the same timescale), in data storage this is a temporal scheme: the sender was you storing the data on your medium at time t, and the receiver is again you but now retrieving the data at time t+x. Thus, the sender does not exist anymore, thus you cannot ask again some data if it's too much corrupted: in data storage, if a data is corrupted, it's lost for good, whereas in channel theory, a data can be submitted again if necessary.

Some attempts were made to translate channel theory and error correcting codes theory to data storage, the first being Reed-Solomon which spawned the RAID schema. Then CIRC (Cross-interleaved Reed�Solomon coding) was devised for use on optical discs to recover from scratches, which was necessary for the technology to be usable for consumers. Since then, new less-optimal but a lot faster algorithms such as LDPC, turbo-codes and fountain codes such as RaptorQ were invented (or rediscovered), but they are still marginally researched for data storage.

This project aims to first implement easy tools to evaluate strategies (filetamper.py) and file fixity (ie, detect if there are corruptions), and then the goal is to provide an open and easy framework to use different kinds of error correction codes to protect and repair files.

Applications included
-------------------------------

The project currently include the following pure-python applications:

- rfigc.py, a hash auditing tool, similar to md5deep/hashdeep, to compute a database of your files along with their metadata, so that later you can check if they were changed/corrupted.

- header_ecc.py, an error correction code using Reed-Solomon generator/corrector for files headers. The idea is to supplement other more common redundancy tools such as PAR2 (which is quite reliable), by adding more resiliency only on the critical parts of the files: their headers. Using this script, you can significantly higher the chance of recovering headers, which will allow you to at least open the files.

- filetamper.py is a quickly made file corrupter, it will erase or change characters in the specified file. This is useful for testing your various protecting strategies and file formats (eg: is PAR2 really resilient against corruption? Are zip archives still partially extractable after corruption or are rar archives better? etc.). Do not underestimate the usefulness of this tool, as you should always check the resiliency of your file formats and of your file protection strategies before relying on them.

- easy_profiler.py is just a quick and simple profiling tool to get you started quickly on what should be optimized to get more speed, if you want to contribute to the project feel free to propose a pull request! (Cython and other optimizations are welcome as long as they are cross-platform and that an alternative pure-python implementation is also available).

- structural_adaptive_ecc.py, a variable error correction rate encoder (kind of a generalization of header_ecc.py).

Note that all tools are primarily made for command-line usage (type script.py --help to get extended info about the accepted arguments), but you can also use rfigc.py and header_ecc.py with a GUI by using the --gui argument (must be the first and only one argument supplied). The GUI is provided as-is and minimal work will be done to maintain it (the focus will stay on functionality rather than ergonomy).

IMPORTANT: it is CRITICAL that you use the same parameters for correcting mode as when you generated the database/ecc files (this is true for all scripts in this bundle). Of course, some options must be changed: -g must become -c to correct, and --update is a particular case. This works this way on purpose for mainly two reasons: first because it is very hard to autodetect the parameters from a database file alone and it would produce lots of false positives, and secondly (the primary reason) is that storing parameters inside the database file is highly unresilient against corruption (if this part of the database is tampered, the whole becomes unreadable, while if they are stored outside or in your own memory, the database file is always accessible). Thus, it is advised to write down the parameters you used to generate your database directly on the storage media you will store your database file on (eg: if it's an optical disk, write the parameters on the cover or directly on the disk using a marker), or better memorize them by heart.

Recursive/Relative Files Integrity Generator and Checker in Python (aka RFIGC)
-------------------------------------------------------------------------------------------------------------------
Recursively generate or check the integrity of files by MD5 and SHA1 hashes, size, modification date or by data structure integrity (only for images).

This script is originally meant to be used for data archival, by allowing an easy way to check for silent file corruption. Thus, this script uses relative paths so that you can easily compute and check the same redundant data copied on different mediums (hard drives, optical discs, etc.). This script is not meant for system files corruption notification, but is more meant to be used from times-to-times to check up on your data archives integrity.

This script was made for Python 2.7.6, but it should be easily adaptable to run on Python 3.x.

### Example usage
- To generate the database (only needed once):

```python rfigc.py -i "folderimages" -d "dbhash.csv" -g ```

- To check:

```python rfigc.py -i "folderimages" -d "dbhash.csv" -l log.txt -s ```

- To update your database by appending new files:

```python rfigc.py -i "folderimages" -d "dbhash.csv" -u -a ```

- To update your database by appending new files AND removing inexistent files:

```python rfigc.py -i "folderimages" -d "dbhash.csv" -u -a -r ```

Note that by default, the script is by default in check mode, to avoid wrong manipulations. It will also alert you if you generate over an already existing database file.

### Arguments

```
  -h, --help            show a help message and exit
  -i /path/to/root/folder, --input /path/to/root/folder
                        Path to the root folder from where the scanning will occ
ur.
  -d /some/folder/databasefile.csv, --database /some/folder/databasefile.csv
                        Path to the csv file containing the hash informations.
  -l /some/folder/filename.log, --log /some/folder/filename.log
                        Path to the log file. (Output will be piped to both the
stdout and the log file)
  -s, --structure_check
                        Check images structures for corruption?
  -e /some/folder/errorsfile.csv, --errors_file /some/folder/errorsfile.csv
                        Path to the error file, where errors at checking will be
 stored in CSV for further processing by other softwares (such as file repair so
ftwares).
  -m, --disable_modification_date_checking
                        Disable modification date checking.
  --skip_missing        Skip missing files when checking (useful if you split yo
ur files into several mediums, for example on optical discs with limited capacit
y).
  -g, --generate        Generate the database? (omit this parameter to check ins
tead of generating).
  -f, --force           Force overwriting the database file even if it already e
xists (if --generate).
  -u, --update          Update database (you must also specify --append or --rem
ove).
  -a, --append          Append new files (if --update).
  -r, --remove          Remove missing files (if --update).
```

Header Error Correction Code script
----------------------------------------------------

This script was made to be used in combination with other more common file redundancy generators (such as PAR2, I advise MultiPar). This is an additional layer of protection for your files: by using a higher resiliency rate on the headers of your files, you ensure that you will be probably able to open them in the future, avoiding the "critical spots" (where if you modify just one bit, your whole file may become unreadable, usually bits residing in the headers).

An interesting benefit of this approach is that it has a low storage (and computational) overhead that scales linearly to the number of files, whatever their size is: for example, if we have a set of 40k files for a total size of 60 GB, with a resiliency_rate of 30% and header_size of 1KB (we limit to the first 1K bytes/characters = our file header), then, without counting the hash per block and other meta-data, the final ECC file will be about 2*resiliency_rate * number_of_files * header_size = 24.5 MB. This size can be lower if there are many files smaller than 1KB. This is a pretty low storage overhead to backup the headers of such a big number of files.

The script is pure-python as are its dependencies: it is thus completely cross-platform and open source. However, this imply that it is quite slow, but PyPy v2.5.0 was successfully tested against the script without any modification, and a speed increase of 5x could be observed. This is still slow but at least it's useable for real datasets.

Structural Adaptive Error Correction Encoder
----------------------------------------------------------------

This script implements a variable error correction rate encoder: each file is ecc encoded using a variable resiliency rate -- using a high constant resiliency rate for the header part (resiliency rate stage 1, high), then a variable resiliency rate is applied to the rest of the file's content, with a higher rate near the beginning of the file (resiliency rate stage 2, medium) which progressively decreases until the end of file (resiliency rate stage 3, the lowest).

The idea is that the critical parts of files usually are placed at the top, and data becomes less and less critical along the file. What is meant by critical is both the critical spots (eg: if you tamper only one character of a file's header you have good chances of losing your entire file) and critically encoded information (eg: archive formats usually encode compressed symbols as they go along the file, which means that the first occurrence is encoded, and then the archive simply writes a reference to the symbol. Thus, the first occurrence is encoded at the top, and subsequent encoding of this same data pattern will just be one symbol, and thus it matters less as long as the original symbol is correctly encoded and its information preserved, we can always try to restore the reference symbols later).

This variable error correction rate would allow to protect more the critical parts of a file (the header and the beginning of a file, for example in compressed file formats such as zip this is where the most importantly strings are encoded) for the same amount of storage as a standard constant error correction rate.

Furthermore, the currently designed format of the ecc file would allow two things that are not available in all current file ecc generators such as PAR2: 1- this would allow to partially repair a file, even if not all the blocks can be corrected (in PAR2, a file is repaired only if all blocks can be repaired, which is a shame because there are still other blocks that could be repaired and thus produce a less corrupted file) ; 2- the ecc file format is quite simple and readable, easy to process by any script, which would allow other softwares to also work on it (and it was also done in this way to be more resilient against error corruptions, so that even if an entry is corrupted, other entries are independent and can maybe be used, thus the ecc is very error tolerant).

The script structural-adaptive-ecc.py implements this idea, which can be seen as an extension of header-ecc.py (and in fact the idea was the other way around: structural-adaptive-ecc.py was conceived first but was too complicated, then header-ecc.py was implemented as a working lessened implementation only for headers, and then structural-adaptive-ecc.py was finished using header-ecc.py code progress). It works, it was a bit tested but not extensively, so make sure you test the script by yourself to see if it's robust enough for your needs (any feedback about this would be greatly appreciated!).

Cython implementation
---------------------------------

This section describes how to use the Cython implementation. However, you should first try PyPy, as it did give 10x to 100x speedup over Cython in our case.

A speedy Cython implementation of the Reed-Solomon library is included. It should provide C-speed for all scripts (as long as you use --ecc_algo 1 or 2, not 3 nor 4). It is not needed, since a pure-python implementation is used by default, but it can be useful if you want to encode big datasets of several hundred of GB.

If you want to build it the C/Cython implementation, do the following:

1- Install a C compiler for your platform. On Linux, gcc should already be installed. On Windows, you need to use the Visual Studio C compiler (not MinGW nor Cygwin gcc, they won't work). You can use the "Microsoft Visual C++ Compiler for Python 2.7", and follow these instructions to make it work if you have Python < 2.7.10:

https://github.com/cython/cython/wiki/CythonExtensionsOnWindows

2- cd to this folder (where PyFileFixity resides), and execute the following command:

```python setup.py build_ext --inplace --compiler=msvc```

If everything goes alright, the C compiler will compile the .c files (that were pre-generated by Cython) and you can then use PyFileFixity scripts just as usual and you should see a huge speedup. Else, if it doesn't work, you might need to generate .c files using Cython for your platform (because the pre-generated .c files may be incompatible with your platform). To do that, you just need to install Cython, which is an easy task with nowadays Python distributions such as Anaconda: download 32-bit Anaconda installer (on Windows you should avoid the 64-bit, it may produce weird issues with Cython), then after install, open the Anaconda Command Prompt and execute: ```conda install cython```. This will install all the necessary stuff along the cython library. Then you can simply execute again the command ```python setup.py build_ext --inplace --compiler=msvc``` and it will this time rebuild from scratch, by autodetecting that you have Cython installed, the setup.py script will automatically generate .c files from .pyx files and then .pyd files (binaries) from .c files.

If you get issues, you can see the following post on how to install Cython:

https://github.com/cython/cython/wiki/InstallingOnWindows

Also, use a smaller --max_block_size to greatly speedup the operations! That's the trick used to compute very quickly RS ECC on optical discs. You give a bit of resiliency of course (because blocks are smaller, thus you protect a smaller number of characters per ECC. This should not change much, but in case you get a big bit error burst on a contiguous block, you may lose a whole block at once. That's why using RS255 is better, but it's very time consuming. However, the resiliency ratios still hold, so for any other case of bit-flipping with average-sized bursts, this should not be a problem.)

In case of a catastrophic event
--------------------------------------------

TODO: write more here

In case of a catastrophic event of your data due to the failure of your storage media (eg: your hard drive crashed), then follow the following steps:

1- use dd_rescue to make a full bit-per-bit verbatim copy of your drive before it dies. The nice thing with dd_rescue is that the copy is exact, and also that it can retries or skip in case of bad sectors (it won't crash on your suddenly at half the process).

2- Use testdisk to restore partition or to copy files based on partition filesystem informations.

3- If you could not recover your files, you can try file scraping using photorec or other similar tools as a last resort to extract data based only from files content (no filename, often uncorrect filetype, file boundaries may be wrong so some data may be cut off, etc.).

4- If you used pyFileFixity before the failure of your storage media, you can then use your pre-computed databases to check that files are intact (rfigc.py) and if they aren't, you can recover them (using header_ecc.py and structural_adaptive_ecc.py).


Todo
-------

- Integrate with https://github.com/Dans-labs/bit-recover ? (need to convert the perl script into python...). Note: from my own tests, it doesn't work so well as the author thinks it is, I couldn't even correct a single corruption... Or maybe I am using it the wrong way (but I used the test scripts included, with no modification. That's weird...).

- Speed optimize the Reed-Solomon library? (using Numpy or Cython? But I want to keep a pure python implementation available just in case, or make a Cython implementation that is also compatible with normal python). Use pprofile to check where to optimize first.

Note: PyPy works great, it really speeds things up a lot!

Note2: numpy does not support galois finite fields in polynomials (or in any other numpy construct in fact). So it may be hard to implement using numpy. Try Cython?
http://jeremykun.com/2014/03/13/programming-with-finite-fields/

Note3: some speed optimizations were done (like precomputing every polynomials for any k, so that a variable rate encoder such as in structural_adaptive_ecc.py won't be slowed down), the last big thing to optimize is `polynomial.py:__divmod__()` which is a recursive function (very bad in Python). Should try to flatten this out (in a __while__ or better in a __for__ loop), and then maybe convert to Cython.

Note4: maybe try to parallelize? The problem is that all CPU intensive work is done in classes's methods, and usually parallelization doesn't work on classes...

Note5: still need 10 times speedup in polynomial/ff operations to be reasonable, and 100 times speedup to be really useful for day-to-day. By lowering max_block_size, it becomes usable, but with a 10x speedup it should be really useable. Try to use a more efficient polynomial division algorithm ? Or implement in C/C++ directly (Boost Python?).
http://www.math.uzh.ch/?file&key1=23398
http://en.wikipedia.org/wiki/Horner's_method
http://en.wikipedia.org/wiki/Multiply%E2%80%93accumulate_operation#Fused_multiply.E2.80.93add

Note6: with latest implementations, we have a 100x speedup when using PyPy 2.5.0: on an Intel Core i7 M640 2.80GHz and 4GB RAM on a SSD hard disk, encoding speed is ~600kB/s with --ecc_algo 2, ~900kB/s with --ecc_algo 3 and if you set --max_block_size 150 --ecc_algo 3 you get ~1.5MB/s, which is quite correct (~2 hours to encode 10GB). Not bad!

- header_ecc.py and structural_adaptive_ecc.py enhance tolerance against faulty hash/ecc blocks and faulty ecc entries (eg: when an entrymarker has wrongly spawned somewhere because of a corruption, when fields aren't well delimited etc.). Could just use multiple try-catch blocks and try to skip errors (if it's only one hash/ecc block fields, we can skip to next block. If it's the whole entry, we skip to next entry).

- Implement near-optimal decoders such as LDPC or turbo-codes. Near-optimal decoders are a bit less efficient than Reed-Solomn (they can recover fewer errors), but they are so much faster that it may be worth for huge datasets where the encoding computation time of Reed-Solomon is just impractical. Also another big advantage is that they are less prone to the cliff effect: this means that even if we can't correct the whole message because too much corruption, they may allow to partially correct it nevertheless.
Maybe use this python with numpy library (no compilation): https://github.com/veeresht/CommPy
Also this library includes interleavers, which may be interesting to be more resilient with RS too. However I hardly see how to interleave without the recovery file being less resilient to tampering (because if you interleave, you have to store this interleaving info somewhere, and it will probably be in the ecc recovery file, which will make it less resilient against corruption although the protected files will be more resilient thank's to interleaving...).

- structural_adaptive_ecc.py: --update "change/remove/add" (change will update ecc entries if changed, remove will remove if file is not present anymore, add will encode new files not already in ecc file). For all, use another ecc file: must be different from input ecc file (from which we will streamline read and output to the target ecc file only if meet conditions).

- rfigc.py --recover_from_filescrapping to help in case of file scraping: it will walk through all files in a folder and compare to both hashes in database, and if there's a match, it will copy the file over and assign it its correct name and datestamp into output folder.
