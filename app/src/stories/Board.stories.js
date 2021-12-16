import React from 'react';

import { Board } from '../components/BoardComponent';

export default {
  title: 'Example/Board',
  component: Board,
  argTypes: {
    backgroundColor: { control: 'color' },
  },
};

const Template = (args) => <Board {...args} />;

export const Primary = Template.bind({});
Primary.args = {
  primary: true,
  label: 'Board',
};
