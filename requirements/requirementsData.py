class RequirementData:
    def __init__(self):
        self.id = None
        self.ie_puid = None
        self.section = None
        self.applicability = None
        self.applicability_comment = None
        self.requirement_type = None
        self.requirement_text = None
        self.allowed_verification_methods = None

    def __str__(self):
        return f"{self.id} {self.section} {self.ie_puid} {self.applicability} {self.applicability_comment} {self.requirement_text}"