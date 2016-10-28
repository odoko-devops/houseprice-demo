from behave import *
from hamcrest import *
from datetime import datetime

@given('a house price search engine with July 2016 data')
def step_impl(context):
    pass

@when('I open the search page')
def step_impl(context):
    context.browser.visit("http://192.168.99.100:8080/")

@when('I enter the post code {postcode}')
def step_impl(context, postcode):
    context.browser.fill("query", postcode)

@when('I click the search button')
def step_impl(context):
    button = context.browser.find_by_name("search")

@then('all house prices should be in {postcode}')
def step_impl(context, postcode):
    elements = context.browser.find_by_css(".result")
    for element in elements:
        assert_that(element.value, starts_with(postcode))


def parse_date(date):
    return datetime.strptime(date, "%Y-%M-%DT%H:%m:%sZ")

@then('all house prices should be for sales between {startdate} and {enddate}')
def step_impl(context, startdate, enddate):
    startdate = parse_date(startdate)
    enddate = parse_date(enddate)
    elements = context.browser.find_by_css(".result")
    for element in elements:
        date = parse_date(element.value)
        assert_that(date, is_greater_than(startdate))
        assert_that(date, is_less_than(enddate))


@when('I enter a start date of {startdate}')
def step_impl(context, startdate):
    context.browser.fill("startdate", startdate)

@when('I enter an end date of {enddate}')
def step_impl(context, enddate):
    context.browser.fill("enddate", enddate)
