import React from 'react'
import { Provider } from 'react-redux'
import { mount } from 'enzyme'
import configureStore from 'redux-mock-store'

import { actionTypes } from '../../features/counter'
import Counter from './Counter'

describe('Counter', () => {
  const mockStore = configureStore([])
  const store = mockStore({
    count: {
      value: 42,
    },
  })

  // Add jest mock spy to watch for store.dispatch method. See https://jestjs.io/docs/en/jest-object#jestspyonobject-methodname for more info
  jest.spyOn(store, 'dispatch')

  beforeEach(() => {
    // Clear any saved mock data from previous tests, because jest saves calls data for spies and mocks, https://jestjs.io/docs/en/mock-function-api#mockfnmockclear
    store.dispatch.mockClear()
  })

  it('renders without crashing.', () => {
    const wrapper = mount(
      <Provider store={store}>
        <Counter />
      </Provider>
    )

    const countValue = wrapper.find('strong').text()
    expect(countValue).toBe('42')
  })

  it('should be possible to increment counter.', () => {
    const wrapper = mount(
      <Provider store={store}>
        <Counter />
      </Provider>
    )

    wrapper
      .find('button')
      .filter({ 'data-qa': 'increment-counter' })
      .simulate('click')

    expect(store.dispatch).toBeCalledTimes(1)

    expect(store.dispatch).toBeCalledWith({
      type: actionTypes.INCREMENT_COUNTER,
    })
  })

  it('should be possible to decrement counter.', () => {
    const wrapper = mount(
      <Provider store={store}>
        <Counter />
      </Provider>
    )

    wrapper
      .find('button')
      .filter({ 'data-qa': 'decrement-counter' })
      .simulate('click')

    expect(store.dispatch).toHaveBeenCalledTimes(1)

    expect(store.dispatch).toHaveBeenCalledWith({
      type: actionTypes.DECREMENT_COUNTER,
    })
  })
})
