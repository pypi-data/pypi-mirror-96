import os

# extract path to the config file
pwd_config_file = os.path.realpath(__file__)
config_file_path = '/'.join(pwd_config_file.split('/')[:-1])

# specify full path to corresponding executables at the right side of colon
config_dict = {'config_file_path'       : config_file_path,
               'bowtie2'                : 'bowtie2',
               'bowtie2_build'          : 'bowtie2-build',
               'samtools'               : 'samtools',
               'blastn'                 : 'blastn',
               'makeblastdb'            : 'makeblastdb',
               'spades'                 : 'spades.py',
               'get_sankey_plot_R'      : '%s/get_sankey_plot.R' % config_file_path
               }
