from datetime import datetime
from discord import User
from typing import Union

from cogs.globals import loop

from util.string import datetime_to_dict

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class CaseNumber:
    def __init__(self, case_numbers):
        self._case_numbers = case_numbers
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Suggestion Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_suggestion_cases_sync(self):
        """Synchronously retrieves all the suggestion cases that have been submitted

        Returns
        -------
            dict
                A JSON object of suggestion cases
        """

        # Default
        default = {
            "number": 1,
            "cases": {}
        }

        # Get suggestion data
        suggestion_data = self._case_numbers.find_one({"_id": "suggestions"})
        if not suggestion_data:
            self._case_numbers.insert_one({"_id": "suggestions"})
            self.set_suggestion_cases_sync(default)
            suggestion_data = default
        return suggestion_data
    
    def set_suggestion_cases_sync(self, suggestion_cases):
        """Synchronously sets the suggestion case data

        Parameters
        ----------
            suggestion_cases : dict
                A JSON object of suggestion cases
        """
        self._case_numbers.update_one(
            {"_id": "suggestions"},
            {"$set": suggestion_cases},
            upsert = False
        )
    
    def get_suggestion_number_sync(self):
        """Synchronously retrieves the current suggestion case number

        Returns
        -------
            int
                The current suggestion case number
        """
        suggestion_data = self.get_suggestion_cases_sync()
        return suggestion_data["number"]
    
    def add_suggestion_sync(self, submitter : Union[User, str], suggestion):
        """Synchronously adds a new suggestion

        Parameters
        ----------
            submitter : str or User
                The User who submitted the suggestion
            suggestion : str
                The submitted suggestion
        """
        suggestion_data = self.get_suggestion_cases_sync()

        # Get the current number and then update it
        number = suggestion_data["number"]
        suggestion_data["number"] += 1

        # Add the suggestion
        suggestion_data["cases"][str(number)] = {
            "suggestion": suggestion,
            "author": submitter if isinstance(submitter, str) else str(submitter.id),
            "time": datetime_to_dict(datetime.now()),
            "seen": None
        }
        self.set_suggestion_cases_sync(suggestion_data)
    
    def get_suggestion_sync(self, suggestion_number):
        """Synchronously retrieves the suggestion associated with the specified number

        Parameters
        ----------
            suggestion_number : int
                The suggestion case number to get
        
        Returns
        -------
            suggestion_case : dict or None
                The suggestion case associated with the specified number
                If None is returned, there was no case found with the number
        """
        suggestion_data = self.get_suggestion_cases_sync()
        if str(suggestion_number) in suggestion_data["cases"]:
            return suggestion_data["cases"][str(suggestion_number)]
        return None
    
    def mark_suggestion_seen_sync(self, suggestion_number, developer : Union[User, str]):
        """Synchronously marks the suggestion associated with the specified number as seen

        Parameters
        ----------
            suggestion_number : int
                The suggestion case number to mark as seen
            developer : str or User
                The developer who marked the suggestion case as seen
        """
        suggestion_data = self.get_suggestion_cases_sync()
        if str(suggestion_number) in suggestion_data["cases"]:
            suggestion_data["cases"][str(suggestion_number)]["seen"] = developer if isinstance(developer, str) else str(developer.id)
            self.set_suggestion_cases_sync(suggestion_data)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    async def get_suggestion_cases(self):
        """Asynchronously retrieves all the suggestion cases that have been submitted

        Returns
        -------
            dict
                A JSON object of suggestion cases
        """
        return await loop.run_in_executor(None, self.get_suggestion_cases_sync)
    
    async def set_suggestion_cases(self, suggestion_cases):
        """Asynchronously sets the suggestion case data

        Parameters
        ----------
            suggestion_cases : dict
                A JSON object of suggestion cases
        """
        await loop.run_in_executor(None, self.set_suggestion_cases_sync, suggestion_cases)

    async def get_suggestion_number(self):
        """Asynchronously retrieves the current suggestion case number

        Returns
        -------
            int
                The current suggestion case number
        """
        return await loop.run_in_executor(None, self.get_suggestion_number_sync)
    
    async def add_suggestion(self, submitter : Union[User, str], suggestion):
        """Asynchronously adds a new suggestion

        Parameters
        ----------
            submitter : str or User
                The User who submitted the suggestion
            suggestion : str
                The submitted suggestion
        """
        await loop.run_in_executor(None, self.add_suggestion_sync, submitter, suggestion)
    
    async def get_suggestion(self, suggestion_number):
        """Asynchronously retrieves the suggestion associated with the specified number

        Parameters
        ----------
            suggestion_number : int
                The suggestion case number to get
        
        Returns
        -------
            suggestion_case : dict or None
                The suggestion case associated with the specified number
                If None is returned, there was no case found with the number
        """
        return await loop.run_in_executor(None, self.get_suggestion_sync, suggestion_number)
    
    async def mark_suggestion_seen(self, suggestion_number, developer : Union[User, str]):
        """Asynchronously marks the suggestion associated with the specified number as seen

        Parameters
        ----------
            suggestion_number : int
                The suggestion case number to mark as seen
            developer : str or User
                The developer who marked the suggestion case as seen
        """
        await loop.run_in_executor(None, self.mark_suggestion_seen_sync, suggestion_number, developer)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Bug Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_bug_cases_sync(self):
        """Synchronously retrieves all the bug cases that have been reported

        Returns
        -------
            dict
                A JSON object of bug cases
        """
        
        # Default
        default = {
            "number": 1,
            "cases": {}
        }

        # Get bug data
        bug_data = self._case_numbers.find_one({"_id": "bugs"})
        if not bug_data:
            self._case_numbers.insert_one({"_id": "bugs"})
            self.set_bug_cases_sync(default)
            bug_data = default
        return bug_data
    
    def set_bug_cases_sync(self, bug_cases):
        """Synchronously sets the bug case data

        Parameters
        ----------
            bug_cases : dict
                A JSON object of bug cases
        """
        self._case_numbers.update_one(
            {"_id": "bugs"},
            {"$set": bug_cases},
            upsert = False
        )
    
    def get_bug_number_sync(self):
        """Synchronously retrieves the current bug case number

        Returns
        -------
            int
                The current bug case number
        """
        bug_data = self.get_bug_cases_sync()
        return bug_data["number"]
    
    def add_bug_sync(self, source_type, source, reporter : Union[User, str], bug_description):
        """Synchronously adds a new bug

        Parameters
        ----------
            source_type : str
                The type of source of the bug, either website or bot
            source : str
                The specific source of the bug
            reporter : str or User
                The User who reported the bug
            bug_description : str
                A description of the bug itself
        """
        bug_data = self.get_bug_cases_sync()

        # Get the current number and then update it
        number = bug_data["number"]
        bug_data["number"] += 1

        # Add the bug
        bug_data["cases"][str(number)] = {
            "bug": bug_description,
            "source_type": source_type,
            "source": source,
            "author": reporter if isinstance(reporter, str) else str(reporter.id),
            "time": datetime_to_dict(datetime.now()),
            "seen": None
        }
        self.set_bug_cases_sync(bug_data)
    
    def get_bug_sync(self, bug_number):
        """Synchronously retrieves the bug associated with the specified number

        Parameters
        ----------
            bug_number : int
                The bug case number to get
        
        Returns
        -------
            bug_case : dict or None
                The bug case associated with the specified number
                If None is returned, there was no case found with that number
        """
        bug_data = self.get_bug_cases_sync()
        if str(bug_number) in bug_data["cases"]:
            return bug_data["cases"][str(bug_number)]
        return None
    
    def mark_bug_seen_sync(self, bug_number, developer : Union[User, str]):
        """Synchronously marks the bug associated with the specified number as seen

        Parameters
        ----------
            bug_number : int
                The bug case number to mark as seen
            developer : str or User
                The developer who marked the bug case as seen
        """
        bug_data = self.get_bug_cases_sync()
        if str(bug_number) in bug_data["cases"]:
            bug_data["cases"][str(bug_number)]["seen"] = developer if isinstance(developer, str) else str(developer.id)
            self.set_bug_cases_sync(bug_data)
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    
    async def get_bug_cases(self):
        """Asynchronously retrieves all the bug cases that have been reported

        Returns
        -------
            dict
                A JSON object of bug cases
        """
        return await loop.run_in_executor(None, self.get_bug_cases_sync)
    
    async def set_bug_cases(self, bug_cases):
        """Asynchronously sets the bug case data

        Parameters
        ----------
            bug_cases : dict
                A JSON object of bug cases
        """
        await loop.run_in_executor(None, self.set_bug_cases_sync, bug_cases)

    async def get_bug_number(self):
        """Asynchronously retrieves the current bug case number

        Returns
        -------
            int
                The current bug case number
        """
        return await loop.run_in_executor(None, self.get_bug_number_sync)
    
    async def add_bug(self, source_type, source, reporter : Union[User, str], bug_description):
        """Asynchronously adds a new bug

        Parameters
        ----------
            source_type : str
                The type of source of the bug, either website or bot
            source : str
                The specific source of the bug
            reporter : str or User
                The User who reported the bug
            bug_description : str
                A description of the bug itself
        """
        await loop.run_in_executor(None, self.add_bug_sync, source_type, source, reporter, bug_description)
    
    async def get_bug(self, bug_number):
        """Asynchronously retrieves the bug associated with the specified number

        Parameters
        ----------
            bug_number : int
                The bug case number to get
        
        Returns
        -------
            bug_case : dict or None
                The bug case associated with the specified number
                If None is returned, there was no case found with that number
        """
        return await loop.run_in_executor(None, self.get_bug_sync, bug_number)
    
    async def mark_bug_seen(self, bug_number, developer : Union[User, str]):
        """Asynchronously marks the bug associated with the specified number as seen

        Parameters
        ----------
            bug_number : int
                The bug case number to mark as seen
            developer : str or User
                The developer who marked the bug case as seen
        """
        await loop.run_in_executor(None, self.mark_bug_seen_sync, bug_number, developer)