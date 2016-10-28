from behave import *
from splinter import Browser


def before_scenario(context, scenario):
    context.browser = Browser("phantomjs")
    context.iframe = None