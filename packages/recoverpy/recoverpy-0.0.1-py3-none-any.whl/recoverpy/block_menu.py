import py_cui

import recoverpy.menu_with_block_display as BLOCK_DISPLAY_MENU

import recoverpy.logger as LOGGER
import recoverpy.saver as SAVER


class BlockMenu(BLOCK_DISPLAY_MENU.MenuWithBlockDisplay):
    """Block menu is called in order to navigate more easily through partition blocks
    and eventually save multiple results in the same file.

    Args:
        BLOCK_DISPLAY_MENU (MenuWithBlockDisplay): Composition to inherit block display
        methods.

    Attributes:
        saved_blocks_dict (dict): Used to store block numbers associated with their text
            contents. Will be used to save it in a file.
        current_block (int): Partition block number currently displayed.
    """

    def __init__(self, master: py_cui.PyCUI, partition: str, initial_block: int):
        """Constructor for Block menu

        Args:
            master (py_cui.PyCUI): PyCUI constructor
            partition (str): System partition to search
            initial_block (int): Initial partition block number that will be displayed.
        """

        self.master = master

        self.partition = partition

        LOGGER.write("info", "Starting 'BlockMenu' CUI window")

        self.saved_blocks_dict = {}

        self.current_block = initial_block

        self.previous_button = self.master.add_button(
            "<",
            0,
            0,
            row_span=9,
            column_span=1,
            padx=1,
            pady=0,
            command=self.display_previous_block,
        )
        self.next_button = self.master.add_button(
            ">",
            0,
            9,
            row_span=9,
            column_span=1,
            padx=1,
            pady=0,
            command=self.display_next_block,
        )

        self.result_content_box = self.master.add_text_block(
            "Block content:", 0, 1, row_span=9, column_span=8, padx=1, pady=0
        )
        self.result_content_box.set_title(
            "Block {current_block}".format(current_block=str(self.current_block))
        )

        # Display initial block at opening
        self.display_block(self.current_block)

        self.add_result_button = self.master.add_button(
            "Add current block to file",
            9,
            0,
            row_span=1,
            column_span=5,
            padx=1,
            pady=0,
            command=self.add_block_to_file,
        )

        self.save_file_button = self.master.add_button(
            "Save file",
            9,
            5,
            row_span=1,
            column_span=3,
            padx=1,
            pady=0,
            command=self.save_file,
        )

        self.go_back_button = self.master.add_button(
            "Go back to previous menu",
            9,
            8,
            row_span=1,
            column_span=2,
            padx=1,
            pady=0,
            command=self.master.stop,
        )

    def add_block_to_file(self):
        """Stores currently displayed result in a dict to save it later."""

        if self.current_block in self.saved_blocks_dict:
            return

        self.master.show_message_popup("", "Result added to file")
        self.saved_blocks_dict[self.current_block] = self.current_result
        LOGGER.write(
            "debug",
            "Stored block {block} for future save".format(block=self.current_block),
        )

    def save_file(self):
        """Function called by user.
        Bundles results saving + popup message.
        """

        len_results = len(self.saved_blocks_dict)

        if len_results == 0:
            self.master.show_message_popup("", "No result to save yeet")
            return
        elif len_results == 1:
            self.master.show_message_popup("", "Result saved")
        else:
            self.master.show_message_popup(
                "", "{len_results} results saved".format(len_results=len_results)
            )

        SAVER.save_result_dict(self.saved_blocks_dict)
