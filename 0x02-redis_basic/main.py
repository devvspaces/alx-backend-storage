#!/usr/bin/env python3
"""
Main file
"""
get_page = __import__('web').get_page

url = 'https://www.digitalocean.com/community/tutorials/how-to-install-mysql-on-ubuntu-20-04'

get_page(url)
